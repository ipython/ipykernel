"""Base class for a kernel that talks to frontends over 0MQ."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import asyncio
import inspect
import itertools
import logging
import os
import socket
import sys
import threading
import time
import typing as t
import uuid
import warnings
from datetime import datetime
from functools import partial
from signal import SIGINT, SIGTERM, Signals, default_int_handler, signal

from .thread import CONTROL_THREAD_NAME

if sys.platform != "win32":
    from signal import SIGKILL
else:
    SIGKILL = "windown-SIGKILL-sentinel"


try:
    # jupyter_client >= 5, use tz-aware now
    from jupyter_client.session import utcnow as now
except ImportError:
    # jupyter_client < 5, use local now()
    now = datetime.now

import psutil
import zmq
from IPython.core.error import StdinNotImplementedError
from jupyter_client.session import Session
from tornado import ioloop
from tornado.queues import Queue, QueueEmpty
from traitlets.config.configurable import SingletonConfigurable
from traitlets.traitlets import (
    Any,
    Bool,
    Dict,
    Float,
    Instance,
    Integer,
    List,
    Unicode,
    default,
    observe,
)
from zmq.eventloop.zmqstream import ZMQStream

from ipykernel.jsonutil import json_clean

from ._version import kernel_protocol_version
from .iostream import OutStream

_AWAITABLE_MESSAGE: str = (
    "For consistency across implementations, it is recommended that `{func_name}`"
    " either be a coroutine function (`async def`) or return an awaitable object"
    " (like an `asyncio.Future`). It might become a requirement in the future."
    " Coroutine functions and awaitables have been supported since"
    " ipykernel 6.0 (2021). {target} does not seem to return an awaitable"
)


def _accepts_parameters(meth, param_names):
    parameters = inspect.signature(meth).parameters
    accepts = dict.fromkeys(param_names, False)

    for param in param_names:
        param_spec = parameters.get(param)
        accepts[param] = (
            param_spec
            and param_spec.kind in [param_spec.KEYWORD_ONLY, param_spec.POSITIONAL_OR_KEYWORD]
        ) or any(p.kind == p.VAR_KEYWORD for p in parameters.values())

    return accepts


class Kernel(SingletonConfigurable):
    """The base kernel class."""

    # ---------------------------------------------------------------------------
    # Kernel interface
    # ---------------------------------------------------------------------------

    # attribute to override with a GUI
    eventloop = Any(None)

    processes: dict[str, psutil.Process] = {}

    @observe("eventloop")
    def _update_eventloop(self, change):
        """schedule call to eventloop from IOLoop"""
        loop = ioloop.IOLoop.current()
        if change.new is not None:
            loop.add_callback(self.enter_eventloop)

    session = Instance(Session, allow_none=True)
    profile_dir = Instance("IPython.core.profiledir.ProfileDir", allow_none=True)
    shell_stream = Instance(ZMQStream, allow_none=True)

    shell_streams: List[t.Any] = List(
        help="""Deprecated shell_streams alias. Use shell_stream

        .. versionchanged:: 6.0
            shell_streams is deprecated. Use shell_stream.
        """
    )

    implementation: str
    implementation_version: str
    banner: str

    @default("shell_streams")
    def _shell_streams_default(self):  # pragma: no cover
        warnings.warn(
            "Kernel.shell_streams is deprecated in ipykernel 6.0. Use Kernel.shell_stream",
            DeprecationWarning,
            stacklevel=2,
        )
        if self.shell_stream is not None:
            return [self.shell_stream]
        return []

    @observe("shell_streams")
    def _shell_streams_changed(self, change):  # pragma: no cover
        warnings.warn(
            "Kernel.shell_streams is deprecated in ipykernel 6.0. Use Kernel.shell_stream",
            DeprecationWarning,
            stacklevel=2,
        )
        if len(change.new) > 1:
            warnings.warn(
                "Kernel only supports one shell stream. Additional streams will be ignored.",
                RuntimeWarning,
                stacklevel=2,
            )
        if change.new:
            self.shell_stream = change.new[0]

    control_stream = Instance(ZMQStream, allow_none=True)

    debug_shell_socket = Any()

    control_thread = Any()
    shell_channel_thread = Any()
    iopub_socket = Any()
    iopub_thread = Any()
    stdin_socket = Any()
    log: logging.Logger = Instance(logging.Logger, allow_none=True)  # type:ignore[assignment]

    # identities:
    int_id = Integer(-1)
    ident = Unicode()

    @default("ident")
    def _default_ident(self):
        return str(uuid.uuid4())

    # This should be overridden by wrapper kernels that implement any real
    # language.
    language_info: dict[str, object] = {}

    # any links that should go in the help menu
    help_links: List[dict[str, str]] = List()

    # Experimental option to break in non-user code.
    # The ipykernel source is in the call stack, so the user
    # has to manipulate the step-over and step-into in a wize way.
    debug_just_my_code = Bool(
        True,
        help="""Set to False if you want to debug python standard and dependent libraries.
        """,
    ).tag(config=True)

    # track associations with current request
    # Private interface

    _darwin_app_nap = Bool(
        True,
        help="""Whether to use appnope for compatibility with OS X App Nap.

        Only affects OS X >= 10.9.
        """,
    ).tag(config=True)

    # track associations with current request
    _allow_stdin = Bool(False)
    _parents: Dict[str, t.Any] = Dict({"shell": {}, "control": {}})
    _parent_ident = Dict({"shell": b"", "control": b""})

    @property
    def _parent_header(self):
        warnings.warn(
            "Kernel._parent_header is deprecated in ipykernel 6. Use .get_parent()",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_parent()

    # Time to sleep after flushing the stdout/err buffers in each execute
    # cycle.  While this introduces a hard limit on the minimal latency of the
    # execute cycle, it helps prevent output synchronization problems for
    # clients.
    # Units are in seconds.  The minimum zmq latency on local host is probably
    # ~150 microseconds, set this to 500us for now.  We may need to increase it
    # a little if it's not enough after more interactive testing.
    _execute_sleep = Float(0.0005).tag(config=True)

    # Frequency of the kernel's event loop.
    # Units are in seconds, kernel subclasses for GUI toolkits may need to
    # adapt to milliseconds.
    _poll_interval = Float(0.01).tag(config=True)

    stop_on_error_timeout = Float(
        0.0,
        config=True,
        help="""time (in seconds) to wait for messages to arrive
        when aborting queued requests after an error.

        Requests that arrive within this window after an error
        will be cancelled.

        Increase in the event of unusually slow network
        causing significant delays,
        which can manifest as e.g. "Run all" in a notebook
        aborting some, but not all, messages after an error.
        """,
    )

    # If the shutdown was requested over the network, we leave here the
    # necessary reply message so it can be sent by our registered atexit
    # handler.  This ensures that the reply is only sent to clients truly at
    # the end of our shutdown process (which happens after the underlying
    # IPython shell's own shutdown).
    _shutdown_message = None

    # This is a dict of port number that the kernel is listening on. It is set
    # by record_ports and used by connect_request.
    _recorded_ports = Dict()

    # Track execution count here. For IPython, we override this to use the
    # execution count we store in the shell.
    execution_count = 0

    msg_types = [
        "execute_request",
        "complete_request",
        "inspect_request",
        "history_request",
        "comm_info_request",
        "kernel_info_request",
        "connect_request",
        "shutdown_request",
        "is_complete_request",
        "interrupt_request",
    ]

    # control channel accepts all shell messages
    # and some of its own
    control_msg_types = [
        *msg_types,
        "debug_request",
        "usage_request",
        "create_subshell_request",
        "delete_subshell_request",
        "list_subshell_request",
    ]

    def __init__(self, **kwargs):
        """Initialize the kernel."""
        super().__init__(**kwargs)

        # Kernel application may swap stdout and stderr to OutStream,
        # which is the case in `IPKernelApp.init_io`, hence `sys.stdout`
        # can already by different from TextIO at initialization time.
        self._stdout: OutStream | t.TextIO = sys.stdout
        self._stderr: OutStream | t.TextIO = sys.stderr

        # Build dict of handlers for message types
        self.shell_handlers = {}
        for msg_type in self.msg_types:
            self.shell_handlers[msg_type] = getattr(self, msg_type)

        self.control_handlers = {}
        for msg_type in self.control_msg_types:
            self.control_handlers[msg_type] = getattr(self, msg_type)

        # Storing the accepted parameters for do_execute, used in execute_request
        self._do_exec_accepted_params = _accepts_parameters(
            self.do_execute, ["cell_meta", "cell_id"]
        )

    async def dispatch_control(self, msg):
        """Dispatch a control request, ensuring only one message is processed at a time."""
        async with asyncio.Lock():
            await self.process_control(msg)

    async def process_control(self, msg):
        """dispatch control requests"""
        if not self.session:
            return
        idents, msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.deserialize(msg, content=True, copy=False)
        except Exception:
            self.log.error("Invalid Control Message", exc_info=True)  # noqa: G201
            return

        self.log.debug("Control received: %s", msg)

        # Set the parent message for side effects.
        self.set_parent(idents, msg, channel="control")
        self._publish_status("busy", "control")

        header = msg["header"]
        msg_type = header["msg_type"]

        handler = self.control_handlers.get(msg_type, None)
        if handler is None:
            self.log.error("UNKNOWN CONTROL MESSAGE TYPE: %r", msg_type)
        else:
            try:
                result = handler(self.control_stream, idents, msg)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                self.log.error("Exception in control handler:", exc_info=True)  # noqa: G201

        if sys.stdout is not None:
            sys.stdout.flush()
        if sys.stderr is not None:
            sys.stderr.flush()
        self._publish_status_and_flush("idle", "control", self.control_stream)

    def should_handle(self, stream, msg, idents):
        """Check whether a shell-channel message should be handled

        Allows subclasses to prevent handling of certain messages (e.g. aborted requests).

        .. versionchanged:: 7
            Subclass should_handle _may_ be async.
            Base class implementation is not async.
        """
        return True

    async def dispatch_shell(self, msg, /, subshell_id: str | None = None):
        """dispatch shell requests"""
        if len(msg) == 1 and msg[0].buffer == b"stop aborting":
            # Dummy "stop aborting" message to stop aborting execute requests on this subshell.
            # This dummy message implementation allows the subshell to abort messages that are
            # already queued in the zmq sockets/streams without having to know any of their
            # details in advance.
            if subshell_id is None:
                self._aborting = False
            else:
                self.shell_channel_thread.manager.set_subshell_aborting(subshell_id, False)
            return

        if not self.session:
            return

        if self._supports_kernel_subshells:
            assert threading.current_thread() not in (
                self.control_thread,
                self.shell_channel_thread,
            )

        idents, msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.deserialize(msg, content=True, copy=False)
        except Exception:
            self.log.error("Invalid Message", exc_info=True)  # noqa: G201
            return

        # Set the parent message for side effects.
        self.set_parent(idents, msg, channel="shell")
        self._publish_status("busy", "shell")

        msg_type = msg["header"]["msg_type"]
        assert msg["header"].get("subshell_id") == subshell_id

        if self._supports_kernel_subshells:
            stream = self.shell_channel_thread.manager.get_subshell_to_shell_channel_socket(
                subshell_id
            )
        else:
            stream = self.shell_stream

        # Only abort execute requests
        if msg_type == "execute_request":
            if subshell_id is None:
                aborting = self._aborting  # type:ignore[unreachable]
            else:
                aborting = self.shell_channel_thread.manager.get_subshell_aborting(subshell_id)
            if aborting:
                self._send_abort_reply(stream, msg, idents)
                self._publish_status_and_flush("idle", "shell", stream)
                return

        # Print some info about this message and leave a '--->' marker, so it's
        # easier to trace visually the message chain when debugging.  Each
        # handler prints its message at the end.
        self.log.debug("\n*** MESSAGE TYPE:%s***", msg_type)
        self.log.debug("   Content: %s\n   --->\n   ", msg["content"])

        should_handle: bool | t.Awaitable[bool] = self.should_handle(stream, msg, idents)
        if inspect.isawaitable(should_handle):
            should_handle = await should_handle
        if not should_handle:
            self._publish_status_and_flush("idle", "shell", stream)
            self.log.debug("Not handling %s:%s", msg_type, msg["header"].get("msg_id"))
            return

        handler = self.shell_handlers.get(msg_type, None)
        if handler is None:
            self.log.warning("Unknown message type: %r", msg_type)
        else:
            self.log.debug("%s: %s", msg_type, msg)
            try:
                self.pre_handler_hook()
            except Exception:
                self.log.debug("Unable to signal in pre_handler_hook:", exc_info=True)
            try:
                result = handler(stream, idents, msg)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                self.log.error("Exception in message handler:", exc_info=True)  # noqa: G201
            except KeyboardInterrupt:
                # Ctrl-c shouldn't crash the kernel here.
                self.log.error("KeyboardInterrupt caught in kernel.")
            finally:
                try:
                    self.post_handler_hook()
                except Exception:
                    self.log.debug("Unable to signal in post_handler_hook:", exc_info=True)

        if sys.stdout is not None:
            sys.stdout.flush()
        if sys.stderr is not None:
            sys.stderr.flush()
        self._publish_status_and_flush("idle", "shell", stream)

    def pre_handler_hook(self):
        """Hook to execute before calling message handler"""
        # ensure default_int_handler during handler call
        self.saved_sigint_handler = signal(SIGINT, default_int_handler)

    def post_handler_hook(self):
        """Hook to execute after calling message handler"""
        signal(SIGINT, self.saved_sigint_handler)

    def enter_eventloop(self):
        """enter eventloop"""
        self.log.info("Entering eventloop %s", self.eventloop)
        # record handle, so we can check when this changes
        eventloop = self.eventloop
        if eventloop is None:
            self.log.info("Exiting as there is no eventloop")
            return

        async def advance_eventloop():
            # check if eventloop changed:
            if self.eventloop is not eventloop:
                self.log.info("exiting eventloop %s", eventloop)
                return
            if self.msg_queue.qsize():
                self.log.debug("Delaying eventloop due to waiting messages")
                # still messages to process, make the eventloop wait
                schedule_next()
                return
            self.log.debug("Advancing eventloop %s", eventloop)
            try:
                eventloop(self)
            except KeyboardInterrupt:
                # Ctrl-C shouldn't crash the kernel
                self.log.error("KeyboardInterrupt caught in kernel")
            if self.eventloop is eventloop:
                # schedule advance again
                schedule_next()

        def schedule_next():
            """Schedule the next advance of the eventloop"""
            # call_later allows the io_loop to process other events if needed.
            # Going through schedule_dispatch ensures all other dispatches on msg_queue
            # are processed before we enter the eventloop, even if the previous dispatch was
            # already consumed from the queue by process_one and the queue is
            # technically empty.
            self.log.debug("Scheduling eventloop advance")
            self.io_loop.call_later(0.001, partial(self.schedule_dispatch, advance_eventloop))

        # begin polling the eventloop
        schedule_next()

    async def do_one_iteration(self):
        """Process a single shell message

        Any pending control messages will be flushed as well

        .. versionchanged:: 5
            This is now a coroutine
        """
        # flush messages off of shell stream into the message queue
        if self.shell_stream:
            self.shell_stream.flush()
        # process at most one shell message per iteration
        await self.process_one(wait=False)

    async def process_one(self, wait=True):
        """Process one request

        Returns None if no message was handled.
        """
        if wait:
            t, dispatch, args = await self.msg_queue.get()
        else:
            try:
                t, dispatch, args = self.msg_queue.get_nowait()
            except (asyncio.QueueEmpty, QueueEmpty):
                return

        if self.control_thread is None and self.control_stream is not None:
            # If there isn't a separate control thread then this main thread handles both shell
            # and control messages. Before processing a shell message we need to flush all control
            # messages and allow them all to be processed.
            await asyncio.sleep(0)
            self.control_stream.flush()

            socket = self.control_stream.socket
            while socket.poll(1):
                await asyncio.sleep(0)
                self.control_stream.flush()

        await dispatch(*args)

    async def dispatch_queue(self):
        """Coroutine to preserve order of message handling

        Ensures that only one message is processing at a time,
        even when the handler is async
        """

        while True:
            try:
                await self.process_one()
            except Exception:
                self.log.exception("Error in message handler")

    _message_counter = Any(
        help="""Monotonic counter of messages
        """,
    )

    @default("_message_counter")
    def _message_counter_default(self):
        return itertools.count()

    def schedule_dispatch(self, dispatch, *args):
        """schedule a message for dispatch"""
        idx = next(self._message_counter)

        self.msg_queue.put_nowait(
            (
                idx,
                dispatch,
                args,
            )
        )
        # ensure the eventloop wakes up
        self.io_loop.add_callback(lambda: None)

    def start(self):
        """register dispatchers for streams"""
        self.io_loop = ioloop.IOLoop.current()
        self.msg_queue: Queue[t.Any] = Queue()
        if not self.shell_channel_thread:
            self.io_loop.add_callback(self.dispatch_queue)

        if self.control_stream:
            self.control_stream.on_recv(self.dispatch_control, copy=False)

        if self.shell_stream:
            if self.shell_channel_thread:
                self.shell_channel_thread.manager.set_on_recv_callback(self.shell_main)
                self.shell_stream.on_recv(self.shell_channel_thread_main, copy=False)
            else:
                self.shell_stream.on_recv(
                    partial(
                        self.schedule_dispatch,
                        self.dispatch_shell,
                    ),
                    copy=False,
                )

        # publish idle status
        self._publish_status("starting", "shell")

    async def shell_channel_thread_main(self, msg):
        """Handler for shell messages received on shell_channel_thread"""
        assert threading.current_thread() == self.shell_channel_thread

        if self.session is None:
            return

        # deserialize only the header to get subshell_id
        # Keep original message to send to subshell_id unmodified.
        _, msg2 = self.session.feed_identities(msg, copy=False)
        try:
            msg3 = self.session.deserialize(msg2, content=False, copy=False)
            subshell_id = msg3["header"].get("subshell_id")

            # Find inproc pair socket to use to send message to correct subshell.
            subshell_manager = self.shell_channel_thread.manager
            socket = subshell_manager.get_shell_channel_to_subshell_socket(subshell_id)
            assert socket is not None
            socket.send_multipart(msg, copy=False)
        except Exception:
            self.log.error("Invalid message", exc_info=True)  # noqa: G201

        if self.shell_stream:
            self.shell_stream.flush()

    async def shell_main(self, subshell_id: str | None, msg):
        """Handler of shell messages for a single subshell"""
        if self._supports_kernel_subshells:
            if subshell_id is None:
                assert threading.current_thread() == threading.main_thread()
            else:
                assert threading.current_thread() not in (
                    self.shell_channel_thread,
                    threading.main_thread(),
                )
            socket_pair = self.shell_channel_thread.manager.get_shell_channel_to_subshell_pair(
                subshell_id
            )
        else:
            assert subshell_id is None
            assert threading.current_thread() == threading.main_thread()
            socket_pair = None

        try:
            # Whilst executing a shell message, do not accept any other shell messages on the
            # same subshell, so that cells are run sequentially. Without this we can run multiple
            # async cells at the same time which would be a nice feature to have but is an API
            # change.
            if socket_pair:
                socket_pair.pause_on_recv()
            await self.dispatch_shell(msg, subshell_id=subshell_id)
        finally:
            if socket_pair:
                socket_pair.resume_on_recv()

    def record_ports(self, ports):
        """Record the ports that this kernel is using.

        The creator of the Kernel instance must call this methods if they
        want the :meth:`connect_request` method to return the port numbers.
        """
        self._recorded_ports = ports

    # ---------------------------------------------------------------------------
    # Kernel request handlers
    # ---------------------------------------------------------------------------

    def _publish_execute_input(self, code, parent, execution_count):
        """Publish the code request on the iopub stream."""
        if not self.session:
            return
        self.session.send(
            self.iopub_socket,
            "execute_input",
            {"code": code, "execution_count": execution_count},
            parent=parent,
            ident=self._topic("execute_input"),
        )

    def _publish_status(self, status, channel, parent=None):
        """send status (busy/idle) on IOPub"""
        if not self.session:
            return
        self.session.send(
            self.iopub_socket,
            "status",
            {"execution_state": status},
            parent=parent or self.get_parent(channel),
            ident=self._topic("status"),
        )

    def _publish_status_and_flush(self, status, channel, stream, parent=None):
        """send status on IOPub and flush specified stream to ensure reply is sent before handling the next reply"""
        self._publish_status(status, channel, parent)
        if stream and hasattr(stream, "flush"):
            stream.flush(zmq.POLLOUT)

    def _publish_debug_event(self, event):
        if not self.session:
            return
        self.session.send(
            self.iopub_socket,
            "debug_event",
            event,
            parent=self.get_parent(),
            ident=self._topic("debug_event"),
        )

    def set_parent(self, ident, parent, channel="shell"):
        """Set the current parent request

        Side effects (IOPub messages) and replies are associated with
        the request that caused them via the parent_header.

        The parent identity is used to route input_request messages
        on the stdin channel.
        """
        self._parent_ident[channel] = ident
        self._parents[channel] = parent

    def get_parent(self, channel=None):
        """Get the parent request associated with a channel.

        .. versionadded:: 6

        Parameters
        ----------
        channel : str
            the name of the channel ('shell' or 'control')

        Returns
        -------
        message : dict
            the parent message for the most recent request on the channel.
        """

        if channel is None:
            # If a channel is not specified, get information from current thread
            if threading.current_thread().name == CONTROL_THREAD_NAME:
                channel = "control"
            else:
                channel = "shell"

        return self._parents.get(channel, {})

    def send_response(
        self,
        stream,
        msg_or_type,
        content=None,
        ident=None,
        buffers=None,
        track=False,
        header=None,
        metadata=None,
        channel=None,
    ):
        """Send a response to the message we're currently processing.

        This accepts all the parameters of :meth:`jupyter_client.session.Session.send`
        except ``parent``.

        This relies on :meth:`set_parent` having been called for the current
        message.
        """
        if not self.session:
            return None
        return self.session.send(
            stream,
            msg_or_type,
            content,
            self.get_parent(channel),
            ident,
            buffers,
            track,
            header,
            metadata,
        )

    def init_metadata(self, parent):
        """Initialize metadata.

        Run at the beginning of execution requests.
        """
        # FIXME: `started` is part of ipyparallel
        # Remove for ipykernel 5.0
        return {
            "started": now(),
        }

    def finish_metadata(self, parent, metadata, reply_content):
        """Finish populating metadata.

        Run after completing an execution request.
        """
        return metadata

    async def execute_request(self, stream, ident, parent):
        """handle an execute_request"""
        if not self.session:
            return
        try:
            content = parent["content"]
            code = content["code"]
            silent = content.get("silent", False)
            store_history = content.get("store_history", not silent)
            user_expressions = content.get("user_expressions", {})
            allow_stdin = content.get("allow_stdin", False)
            cell_meta = parent.get("metadata", {})
            cell_id = cell_meta.get("cellId")
        except Exception:
            self.log.error("Got bad msg: ")
            self.log.error("%s", parent)
            return

        stop_on_error = content.get("stop_on_error", True)

        metadata = self.init_metadata(parent)

        # Re-broadcast our input for the benefit of listening clients, and
        # start computing output
        if not silent:
            self.execution_count += 1
            self._publish_execute_input(code, parent, self.execution_count)

        # Arguments based on the do_execute signature
        do_execute_args = {
            "code": code,
            "silent": silent,
            "store_history": store_history,
            "user_expressions": user_expressions,
            "allow_stdin": allow_stdin,
        }

        if self._do_exec_accepted_params["cell_meta"]:
            do_execute_args["cell_meta"] = cell_meta
        if self._do_exec_accepted_params["cell_id"]:
            do_execute_args["cell_id"] = cell_id

        subshell_id = parent["header"].get("subshell_id")

        # Call do_execute with the appropriate arguments
        reply_content = self.do_execute(**do_execute_args)

        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
        else:
            warnings.warn(
                _AWAITABLE_MESSAGE.format(func_name="do_execute", target=self.do_execute),
                PendingDeprecationWarning,
                stacklevel=1,
            )

        # Flush output before sending the reply.
        if sys.stdout is not None:
            sys.stdout.flush()
        if sys.stderr is not None:
            sys.stderr.flush()
        # FIXME: on rare occasions, the flush doesn't seem to make it to the
        # clients... This seems to mitigate the problem, but we definitely need
        # to better understand what's going on.
        if self._execute_sleep:
            time.sleep(self._execute_sleep)

        # Send the reply.
        reply_content = json_clean(reply_content)
        metadata = self.finish_metadata(parent, metadata, reply_content)

        reply_msg: dict[str, t.Any] = self.session.send(  # type:ignore[assignment]
            stream,
            "execute_reply",
            reply_content,
            parent,
            metadata=metadata,
            ident=ident,
        )

        self.log.debug("%s", reply_msg)

        if not silent and reply_msg["content"]["status"] == "error" and stop_on_error:
            subshell_id = parent["header"].get("subshell_id")
            self._abort_queues(subshell_id)

    def do_execute(
        self,
        code,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=False,
        *,
        cell_meta=None,
        cell_id=None,
    ):
        """Execute user code. Must be overridden by subclasses."""
        raise NotImplementedError

    async def complete_request(self, stream, ident, parent):
        """Handle a completion request."""
        if not self.session:
            return
        content = parent["content"]
        code = content["code"]
        cursor_pos = content["cursor_pos"]

        matches = self.do_complete(code, cursor_pos)
        if inspect.isawaitable(matches):
            matches = await matches
        else:
            warnings.warn(
                _AWAITABLE_MESSAGE.format(func_name="do_complete", target=self.do_complete),
                PendingDeprecationWarning,
                stacklevel=1,
            )

        matches = json_clean(matches)
        self.session.send(stream, "complete_reply", matches, parent, ident)

    def do_complete(self, code, cursor_pos):
        """Override in subclasses to find completions."""
        return {
            "matches": [],
            "cursor_end": cursor_pos,
            "cursor_start": cursor_pos,
            "metadata": {},
            "status": "ok",
        }

    async def inspect_request(self, stream, ident, parent):
        """Handle an inspect request."""
        if not self.session:
            return
        content = parent["content"]

        reply_content = self.do_inspect(
            content["code"],
            content["cursor_pos"],
            content.get("detail_level", 0),
            set(content.get("omit_sections", [])),
        )
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
        else:
            warnings.warn(
                _AWAITABLE_MESSAGE.format(func_name="do_inspect", target=self.do_inspect),
                PendingDeprecationWarning,
                stacklevel=1,
            )

        # Before we send this object over, we scrub it for JSON usage
        reply_content = json_clean(reply_content)
        msg = self.session.send(stream, "inspect_reply", reply_content, parent, ident)
        self.log.debug("%s", msg)

    def do_inspect(self, code, cursor_pos, detail_level=0, omit_sections=()):
        """Override in subclasses to allow introspection."""
        return {"status": "ok", "data": {}, "metadata": {}, "found": False}

    async def history_request(self, stream, ident, parent):
        """Handle a history request."""
        if not self.session:
            return
        content = parent["content"]

        reply_content = self.do_history(**content)
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
        else:
            warnings.warn(
                _AWAITABLE_MESSAGE.format(func_name="do_history", target=self.do_history),
                PendingDeprecationWarning,
                stacklevel=1,
            )

        reply_content = json_clean(reply_content)
        msg = self.session.send(stream, "history_reply", reply_content, parent, ident)
        self.log.debug("%s", msg)

    def do_history(
        self,
        hist_access_type,
        output,
        raw,
        session=None,
        start=None,
        stop=None,
        n=None,
        pattern=None,
        unique=False,
    ):
        """Override in subclasses to access history."""
        return {"status": "ok", "history": []}

    async def connect_request(self, stream, ident, parent):
        """Handle a connect request."""
        if not self.session:
            return
        content = self._recorded_ports.copy() if self._recorded_ports else {}
        content["status"] = "ok"
        msg = self.session.send(stream, "connect_reply", content, parent, ident)
        self.log.debug("%s", msg)

    @property
    def kernel_info(self):
        from .debugger import _is_debugpy_available

        supported_features: list[str] = []
        if self._supports_kernel_subshells:
            supported_features.append("kernel subshells")
        if _is_debugpy_available:
            supported_features.append("debugger")

        return {
            "protocol_version": kernel_protocol_version,
            "implementation": self.implementation,
            "implementation_version": self.implementation_version,
            "language_info": self.language_info,
            "banner": self.banner,
            "help_links": self.help_links,
            "supported_features": supported_features,
        }

    async def kernel_info_request(self, stream, ident, parent):
        """Handle a kernel info request."""
        if not self.session:
            return
        content = {"status": "ok"}
        content.update(self.kernel_info)
        msg = self.session.send(stream, "kernel_info_reply", content, parent, ident)
        self.log.debug("%s", msg)

    async def comm_info_request(self, stream, ident, parent):
        """Handle a comm info request."""
        if not self.session:
            return
        content = parent["content"]
        target_name = content.get("target_name", None)

        # Should this be moved to ipkernel?
        if hasattr(self, "comm_manager"):
            comms = {
                k: dict(target_name=v.target_name)
                for (k, v) in self.comm_manager.comms.items()
                if v.target_name == target_name or target_name is None
            }
        else:
            comms = {}
        reply_content = dict(comms=comms, status="ok")
        msg = self.session.send(stream, "comm_info_reply", reply_content, parent, ident)
        self.log.debug("%s", msg)

    def _send_interrupt_children(self):
        if os.name == "nt":
            self.log.error("Interrupt message not supported on Windows")
        else:
            pid = os.getpid()
            pgid = os.getpgid(pid)
            # Prefer process-group over process
            # but only if the kernel is the leader of the process group
            if pgid and pgid == pid and hasattr(os, "killpg"):
                try:
                    os.killpg(pgid, SIGINT)
                except OSError:
                    os.kill(pid, SIGINT)
                    raise
            else:
                os.kill(pid, SIGINT)

    async def interrupt_request(self, stream, ident, parent):
        """Handle an interrupt request."""
        if not self.session:
            return
        content: dict[str, t.Any] = {"status": "ok"}
        try:
            self._send_interrupt_children()
        except OSError as err:
            import traceback

            content = {
                "status": "error",
                "traceback": traceback.format_stack(),
                "ename": str(type(err).__name__),
                "evalue": str(err),
            }

        self.session.send(stream, "interrupt_reply", content, parent, ident=ident)
        return

    async def shutdown_request(self, stream, ident, parent):
        """Handle a shutdown request."""
        if not self.session:
            return
        content = self.do_shutdown(parent["content"]["restart"])
        if inspect.isawaitable(content):
            content = await content
        else:
            warnings.warn(
                _AWAITABLE_MESSAGE.format(func_name="do_shutdown", target=self.do_shutdown),
                PendingDeprecationWarning,
                stacklevel=1,
            )
        self.session.send(stream, "shutdown_reply", content, parent, ident=ident)
        # same content, but different msg_id for broadcasting on IOPub
        self._shutdown_message = self.session.msg("shutdown_reply", content, parent)

        await self._at_shutdown()

        self.log.debug("Stopping control ioloop")
        if self.control_stream:
            control_io_loop = self.control_stream.io_loop
            control_io_loop.add_callback(control_io_loop.stop)

        self.log.debug("Stopping shell ioloop")
        self.io_loop.add_callback(self.io_loop.stop)
        if self.shell_stream and self.shell_stream.io_loop != self.io_loop:
            shell_io_loop = self.shell_stream.io_loop
            shell_io_loop.add_callback(shell_io_loop.stop)

    def do_shutdown(self, restart):
        """Override in subclasses to do things when the frontend shuts down the
        kernel.
        """
        return {"status": "ok", "restart": restart}

    async def is_complete_request(self, stream, ident, parent):
        """Handle an is_complete request."""
        if not self.session:
            return
        content = parent["content"]
        code = content["code"]

        reply_content = self.do_is_complete(code)
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
        else:
            warnings.warn(
                _AWAITABLE_MESSAGE.format(func_name="do_is_complete", target=self.do_is_complete),
                PendingDeprecationWarning,
                stacklevel=1,
            )
        reply_content = json_clean(reply_content)
        reply_msg = self.session.send(stream, "is_complete_reply", reply_content, parent, ident)
        self.log.debug("%s", reply_msg)

    def do_is_complete(self, code):
        """Override in subclasses to find completions."""
        return {"status": "unknown"}

    async def debug_request(self, stream, ident, parent):
        """Handle a debug request."""
        if not self.session:
            return
        content = parent["content"]
        reply_content = self.do_debug_request(content)
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
        else:
            warnings.warn(
                _AWAITABLE_MESSAGE.format(
                    func_name="do_debug_request", target=self.do_debug_request
                ),
                PendingDeprecationWarning,
                stacklevel=1,
            )
        reply_content = json_clean(reply_content)
        reply_msg = self.session.send(stream, "debug_reply", reply_content, parent, ident)
        self.log.debug("%s", reply_msg)

    def get_process_metric_value(self, process, name, attribute=None):
        """Get the process metric value."""
        try:
            metric_value = getattr(process, name)()
            if attribute is not None:  # ... a named tuple
                return getattr(metric_value, attribute)
            # ... or a number
            return metric_value
        # Avoid littering logs with stack traces
        # complaining about dead processes
        except BaseException:
            return 0

    async def usage_request(self, stream, ident, parent):
        """Handle a usage request."""
        if not self.session:
            return
        reply_content = {"hostname": socket.gethostname(), "pid": os.getpid()}
        current_process = psutil.Process()
        all_processes = [current_process, *current_process.children(recursive=True)]
        # Ensure 1) self.processes is updated to only current subprocesses
        # and 2) we reuse processes when possible (needed for accurate CPU)
        self.processes = {
            process.pid: self.processes.get(process.pid, process)  # type:ignore[misc,call-overload]
            for process in all_processes
        }
        reply_content["kernel_cpu"] = sum(
            [
                self.get_process_metric_value(process, "cpu_percent", None)
                for process in self.processes.values()
            ]
        )
        mem_info_type = "pss" if hasattr(current_process.memory_full_info(), "pss") else "rss"
        reply_content["kernel_memory"] = sum(
            [
                self.get_process_metric_value(process, "memory_full_info", mem_info_type)
                for process in self.processes.values()
            ]
        )
        cpu_percent = psutil.cpu_percent()
        # https://psutil.readthedocs.io/en/latest/index.html?highlight=cpu#psutil.cpu_percent
        # The first time cpu_percent is called it will return a meaningless 0.0 value which you are supposed to ignore.
        if cpu_percent is not None and cpu_percent != 0.0:  # type:ignore[redundant-expr]
            reply_content["host_cpu_percent"] = cpu_percent
        reply_content["cpu_count"] = psutil.cpu_count(logical=True)
        reply_content["host_virtual_memory"] = dict(psutil.virtual_memory()._asdict())
        reply_msg = self.session.send(stream, "usage_reply", reply_content, parent, ident)
        self.log.debug("%s", reply_msg)

    async def do_debug_request(self, msg):
        raise NotImplementedError

    async def create_subshell_request(self, socket, ident, parent) -> None:
        """Handle a create subshell request.

        .. versionadded:: 7
        """
        if not self.session:
            return
        if not self._supports_kernel_subshells:
            self.log.error("Subshells are not supported by this kernel")
            return

        assert threading.current_thread().name == CONTROL_THREAD_NAME

        # This should only be called in the control thread if it exists.
        # Request is passed to shell channel thread to process.
        control_socket = self.shell_channel_thread.manager.control_to_shell_channel.from_socket
        control_socket.send_json({"type": "create"})
        reply = control_socket.recv_json()
        self.session.send(socket, "create_subshell_reply", reply, parent, ident)

    async def delete_subshell_request(self, socket, ident, parent) -> None:
        """Handle a delete subshell request.

        .. versionadded:: 7
        """
        if not self.session:
            return
        if not self._supports_kernel_subshells:
            self.log.error("KERNEL SUBSHELLS NOT SUPPORTED")
            return

        assert threading.current_thread().name == CONTROL_THREAD_NAME

        try:
            content = parent["content"]
            subshell_id = content["subshell_id"]
        except Exception:
            self.log.error("Got bad msg from parent: %s", parent)
            return

        # This should only be called in the control thread if it exists.
        # Request is passed to shell channel thread to process.
        control_socket = self.shell_channel_thread.manager.control_to_shell_channel.from_socket
        control_socket.send_json({"type": "delete", "subshell_id": subshell_id})
        reply = control_socket.recv_json()

        self.session.send(socket, "delete_subshell_reply", reply, parent, ident)

    async def list_subshell_request(self, socket, ident, parent) -> None:
        """Handle a list subshell request.

        .. versionadded:: 7
        """
        if not self.session:
            return
        if not self._supports_kernel_subshells:
            self.log.error("Subshells are not supported by this kernel")
            return

        assert threading.current_thread().name == CONTROL_THREAD_NAME

        # This should only be called in the control thread if it exists.
        # Request is passed to shell channel thread to process.
        control_socket = self.shell_channel_thread.manager.control_to_shell_channel.from_socket
        control_socket.send_json({"type": "list"})
        reply = control_socket.recv_json()

        self.session.send(socket, "list_subshell_reply", reply, parent, ident)

    # ---------------------------------------------------------------------------
    # Protected interface
    # ---------------------------------------------------------------------------

    def _topic(self, topic):
        """prefixed topic for IOPub messages"""
        base = "kernel.%s" % self.ident

        return (f"{base}.{topic}").encode()

    _aborting = Bool(False)

    def _post_dummy_stop_aborting_message(self, subshell_id: str | None) -> None:
        """Post a dummy message to the correct subshell that when handled will unset
        the _aborting flag.
        """
        subshell_manager = self.shell_channel_thread.manager
        socket = subshell_manager.get_shell_channel_to_subshell_socket(subshell_id)
        assert socket is not None

        msg = b"stop aborting"  # Magic string for dummy message.
        socket.send(msg, copy=False)

    def _abort_queues(self, subshell_id: str | None = None):
        # while this flag is true,
        # execute requests will be aborted

        if subshell_id is None:
            self._aborting = True
        else:
            self.shell_channel_thread.manager.set_subshell_aborting(subshell_id, True)
        self.log.info("Aborting queue")

        if self.shell_channel_thread:
            # Only really need to do this if there are messages already queued
            self.shell_channel_thread.io_loop.add_callback(
                self._post_dummy_stop_aborting_message, subshell_id
            )
            return

        # flush streams, so all currently waiting messages
        # are added to the queue
        if self.shell_stream:
            self.shell_stream.flush()

        # Callback to signal that we are done aborting
        # dispatch functions _must_ be async
        async def stop_aborting():
            self.log.info("Finishing abort")
            self._aborting = False

        # put the stop-aborting event on the message queue
        # so that all messages already waiting in the queue are aborted
        # before we reset the flag
        schedule_stop_aborting = partial(self.schedule_dispatch, stop_aborting)

        if self.stop_on_error_timeout:
            # if we have a delay, give messages this long to arrive on the queue
            # before we stop aborting requests
            self.io_loop.call_later(self.stop_on_error_timeout, schedule_stop_aborting)
            # If we have an eventloop, it may interfere with the call_later above.
            # If the loop has a _schedule_exit method, we call that so the loop exits
            # after stop_on_error_timeout, returning to the main io_loop and letting
            # the call_later fire.
            if self.eventloop is not None and hasattr(self.eventloop, "_schedule_exit"):
                self.eventloop._schedule_exit(self.stop_on_error_timeout + 0.01)
        else:
            schedule_stop_aborting()

    def _send_abort_reply(self, stream, msg, idents):
        """Send a reply to an aborted request"""
        if not self.session:
            return
        self.log.info("Aborting %s: %s", msg["header"]["msg_id"], msg["header"]["msg_type"])
        reply_type = msg["header"]["msg_type"].rsplit("_", 1)[0] + "_reply"
        status = {"status": "aborted"}
        md = self.init_metadata(msg)
        md = self.finish_metadata(msg, md, status)
        md.update(status)

        self.session.send(
            stream,
            reply_type,
            metadata=md,
            content=status,
            parent=msg,
            ident=idents,
        )

    def _no_raw_input(self):
        """Raise StdinNotImplementedError if active frontend doesn't support
        stdin."""
        msg = "raw_input was called, but this frontend does not support stdin."
        raise StdinNotImplementedError(msg)

    def getpass(self, prompt="", stream=None):
        """Forward getpass to frontends

        Raises
        ------
        StdinNotImplementedError if active frontend doesn't support stdin.
        """
        if not self._allow_stdin:
            msg = "getpass was called, but this frontend does not support input requests."
            raise StdinNotImplementedError(msg)
        if stream is not None:
            import warnings

            warnings.warn(
                "The `stream` parameter of `getpass.getpass` will have no effect when using ipykernel",
                UserWarning,
                stacklevel=2,
            )
        return self._input_request(
            prompt,
            self._parent_ident["shell"],
            self.get_parent("shell"),
            password=True,
        )

    def raw_input(self, prompt=""):
        """Forward raw_input to frontends

        Raises
        ------
        StdinNotImplementedError if active frontend doesn't support stdin.
        """
        if not self._allow_stdin:
            msg = "raw_input was called, but this frontend does not support input requests."
            raise StdinNotImplementedError(msg)
        return self._input_request(
            str(prompt),
            self._parent_ident["shell"],
            self.get_parent("shell"),
            password=False,
        )

    def _input_request(self, prompt, ident, parent, password=False):
        # Flush output before making the request.
        if sys.stdout is not None:
            sys.stdout.flush()
        if sys.stderr is not None:
            sys.stderr.flush()

        # flush the stdin socket, to purge stale replies
        while True:
            try:
                self.stdin_socket.recv_multipart(zmq.NOBLOCK)
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    break
                raise

        # Send the input request.
        assert self.session is not None
        content = json_clean(dict(prompt=prompt, password=password))
        self.session.send(self.stdin_socket, "input_request", content, parent, ident=ident)

        # Await a response.
        while True:
            try:
                # Use polling with select() so KeyboardInterrupts can get
                # through; doing a blocking recv() means stdin reads are
                # uninterruptible on Windows. We need a timeout because
                # zmq.select() is also uninterruptible, but at least this
                # way reads get noticed immediately and KeyboardInterrupts
                # get noticed fairly quickly by human response time standards.
                rlist, _, xlist = zmq.select([self.stdin_socket], [], [self.stdin_socket], 0.01)
                if rlist or xlist:
                    ident, reply = self.session.recv(self.stdin_socket)
                    if (ident, reply) != (None, None):
                        break
            except KeyboardInterrupt:
                # re-raise KeyboardInterrupt, to truncate traceback
                msg = "Interrupted by user"
                raise KeyboardInterrupt(msg) from None
            except Exception:
                self.log.warning("Invalid Message:", exc_info=True)

        try:
            value = reply["content"]["value"]  # type:ignore[index]
        except Exception:
            self.log.error("Bad input_reply: %s", parent)
            value = ""
        if value == "\x04":
            # EOF
            raise EOFError
        return value

    def _signal_children(self, signum):
        """
        Send a signal to all our children

        Like `killpg`, but does not include the current process
        (or possible parents).
        """
        sig_rep = f"{Signals(signum)!r}"
        for p in self._process_children():
            self.log.debug("Sending %s to subprocess %s", sig_rep, p)
            try:
                if signum == SIGTERM:
                    p.terminate()
                elif signum == SIGKILL:
                    p.kill()
                else:
                    p.send_signal(signum)
            except psutil.NoSuchProcess:
                pass

    def _process_children(self):
        """Retrieve child processes in the kernel's process group

        Avoids:
        - including parents and self with killpg
        - including all children that may have forked-off a new group
        """
        kernel_process = psutil.Process()
        all_children = kernel_process.children(recursive=True)
        if os.name == "nt":
            return all_children
        kernel_pgid = os.getpgrp()
        process_group_children = []
        for child in all_children:
            try:
                child_pgid = os.getpgid(child.pid)
            except OSError:
                pass
            else:
                if child_pgid == kernel_pgid:
                    process_group_children.append(child)
        return process_group_children

    async def _progressively_terminate_all_children(self):
        sleeps = (0.01, 0.03, 0.1, 0.3, 1, 3, 10)
        if not self._process_children():
            self.log.debug("Kernel has no children.")
            return

        for signum in (SIGTERM, SIGKILL):
            for delay in sleeps:
                children = self._process_children()
                if not children:
                    self.log.debug("No more children, continuing shutdown routine.")
                    return
                # signals only children, not current process
                self._signal_children(signum)
                self.log.debug(
                    "Will sleep %s sec before checking for children and retrying. %s",
                    delay,
                    children,
                )
                await asyncio.sleep(delay)

    async def _at_shutdown(self):
        """Actions taken at shutdown by the kernel, called by python's atexit."""
        try:
            await self._progressively_terminate_all_children()
        except Exception as e:
            self.log.exception("Exception during subprocesses termination %s", e)

        finally:
            if self._shutdown_message is not None and self.session:
                self.session.send(
                    self.iopub_socket,
                    self._shutdown_message,
                    ident=self._topic("shutdown"),
                )
                self.log.debug("%s", self._shutdown_message)
            if self.control_stream:
                self.control_stream.flush(zmq.POLLOUT)

    @property
    def _supports_kernel_subshells(self):
        return self.shell_channel_thread is not None
