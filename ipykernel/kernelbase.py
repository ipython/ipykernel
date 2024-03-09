"""Base class for a kernel that talks to frontends over 0MQ."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import asyncio
import inspect
import itertools
import logging
import os
import queue
import sys
import threading
import time
import typing as t
import uuid
import warnings
from datetime import datetime
from functools import partial
from signal import SIGINT, SIGTERM, Signals, signal

from .control import CONTROL_THREAD_NAME

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
from anyio import TASK_STATUS_IGNORED, create_task_group, sleep, to_thread
from anyio.abc import TaskStatus
from IPython.core.error import StdinNotImplementedError
from jupyter_client.session import Session
from traitlets.config.configurable import SingletonConfigurable
from traitlets.traitlets import (
    Any,
    Bool,
    Dict,
    Float,
    Instance,
    Integer,
    List,
    Set,
    Unicode,
    default,
    observe,
)

from ipykernel.jsonutil import json_clean

from ._version import kernel_protocol_version
from .iostream import OutStream


def _accepts_parameters(meth, param_names):
    parameters = inspect.signature(meth).parameters
    accepts = {param: False for param in param_names}

    for param in param_names:
        param_spec = parameters.get(param)
        accepts[param] = (
            param_spec
            and param_spec.kind in [param_spec.KEYWORD_ONLY, param_spec.POSITIONAL_OR_KEYWORD]
        ) or any(p.kind == p.VAR_KEYWORD for p in parameters.values())

    return accepts


class Kernel(SingletonConfigurable):
    """The base kernel class."""

    _aborted_time: float

    # ---------------------------------------------------------------------------
    # Kernel interface
    # ---------------------------------------------------------------------------

    # attribute to override with a GUI
    eventloop = Any(None)

    processes: dict[str, psutil.Process] = {}

    session = Instance(Session, allow_none=True)
    profile_dir = Instance("IPython.core.profiledir.ProfileDir", allow_none=True)
    shell_socket = Instance(zmq.asyncio.Socket, allow_none=True)

    shell_streams: List[t.Any] = List(
        help="""Deprecated shell_streams alias. Use shell_stream

        .. versionchanged:: 6.0
            shell_streams is deprecated. Use shell_stream.
        """
    )

    implementation: str
    implementation_version: str
    banner: str

    _is_test = Bool(False)

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

    control_socket = Instance(zmq.asyncio.Socket, allow_none=True)
    control_tasks: t.Any = List()

    debug_shell_socket = Any()

    control_thread = Any()
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

    # set of aborted msg_ids
    aborted = Set()

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
        # deprecated:
        "apply_request",
    ]
    # add deprecated ipyparallel control messages
    control_msg_types = [
        *msg_types,
        "clear_request",
        "abort_request",
        "debug_request",
        "usage_request",
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
        # Ensure only one control message is processed at a time
        async with asyncio.Lock():
            await self.process_control(msg)

    async def process_control(self):
        try:
            while True:
                await self.process_control_message()
        except BaseException as e:
            if self.control_stop.is_set():
                return
            raise e

    async def process_control_message(self, msg=None):
        """dispatch control requests"""
        assert self.control_socket is not None
        assert self.session is not None

        msg = msg or await self.control_socket.recv_multipart()
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

        sys.stdout.flush()
        sys.stderr.flush()
        self._publish_status("idle", "control")
        # flush to ensure reply is sent
        if self.control_stream:
            self.control_stream.flush(zmq.POLLOUT)

    async def should_handle(self, stream, msg, idents):
        """Check whether a shell-channel message should be handled

        Allows subclasses to prevent handling of certain messages (e.g. aborted requests).
        """
        msg_id = msg["header"]["msg_id"]
        if msg_id in self.aborted:
            # is it safe to assume a msg_id will not be resubmitted?
            self.aborted.remove(msg_id)
            await self._send_abort_reply(stream, msg, idents)
            return False
        return True

    def pre_handler_hook(self):
        """Hook to execute before calling message handler"""
        # ensure default_int_handler during handler call

    async def enter_eventloop(self):
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
            self.log.debug("Advancing eventloop %s", eventloop)
            try:
                eventloop(self)
            except KeyboardInterrupt:
                # Ctrl-C shouldn't crash the kernel
                self.log.error("KeyboardInterrupt caught in kernel")
            if self.eventloop is eventloop:
                # schedule advance again
                await schedule_next()

        async def schedule_next():
            """Schedule the next advance of the eventloop"""
            # flush the eventloop every so often,
            # giving us a chance to handle messages in the meantime
            self.log.debug("Scheduling eventloop advance")
            await sleep(0.001)
            await advance_eventloop()

        # begin polling the eventloop
        await schedule_next()

    _message_counter = Any(
        help="""Monotonic counter of messages
        """,
    )

    @default("_message_counter")
    def _message_counter_default(self):
        return itertools.count()

    async def shell_main(self):
        async with create_task_group() as tg:
            tg.start_soon(self.process_shell)
            await to_thread.run_sync(self.shell_stop.wait)
            tg.cancel_scope.cancel()

    async def process_shell(self):
        try:
            while True:
                await self.process_shell_message()
        except BaseException as e:
            if self.shell_stop.is_set():
                return
            raise e

    async def process_shell_message(self, msg=None):
        assert self.shell_socket is not None
        assert self.session is not None

        no_msg = msg is None if self._is_test else not await self.shell_socket.poll(0)

        msg = msg or await self.shell_socket.recv_multipart()
        received_time = time.monotonic()
        idents, msg = self.session.feed_identities(msg, copy=True)
        try:
            msg = self.session.deserialize(msg, content=True, copy=True)
        except BaseException:
            self.log.error("Invalid Message", exc_info=True)  # noqa: G201
            return

        # Set the parent message for side effects.
        self.set_parent(idents, msg, channel="shell")
        self._publish_status("busy", "shell")

        msg_type = msg["header"]["msg_type"]

        # Only abort execute requests
        if self._aborting and msg_type == "execute_request":
            if not self.stop_on_error_timeout:
                if no_msg:
                    self._aborting = False
            elif received_time - self._aborted_time > self.stop_on_error_timeout:
                self._aborting = False
            if self._aborting:
                await self._send_abort_reply(self.shell_socket, msg, idents)
                self._publish_status("idle", "shell")
                return

        # Print some info about this message and leave a '--->' marker, so it's
        # easier to trace visually the message chain when debugging.  Each
        # handler prints its message at the end.
        self.log.debug("\n*** MESSAGE TYPE:%s***", msg_type)
        self.log.debug("   Content: %s\n   --->\n   ", msg["content"])

        if not await self.should_handle(self.shell_socket, msg, idents):
            return

        handler = self.shell_handlers.get(msg_type)
        if handler is None:
            self.log.warning("Unknown message type: %r", msg_type)
        else:
            self.log.debug("%s: %s", msg_type, msg)
            try:
                self.pre_handler_hook()
            except Exception:
                self.log.debug("Unable to signal in pre_handler_hook:", exc_info=True)
            try:
                result = handler(self.shell_socket, idents, msg)
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

        sys.stdout.flush()
        sys.stderr.flush()
        self._publish_status("idle", "shell")

    async def control_main(self):
        async with create_task_group() as tg:
            for task in self.control_tasks:
                tg.start_soon(task)
            tg.start_soon(self.process_control)
            await to_thread.run_sync(self.control_stop.wait)
            tg.cancel_scope.cancel()

    def post_handler_hook(self):
        """Hook to execute after calling message handler"""
        signal(SIGINT, self.saved_sigint_handler)

    async def dispatch_queue(self):
        """Coroutine to preserve order of message handling

        Ensures that only one message is processing at a time,
        even when the handler is async
        """

        while True:
            try:
                await self.process_one()
            except Exception:
                self.log.error("Exception in control handler:", exc_info=True)  # noqa: G201

        sys.stdout.flush()
        sys.stderr.flush()
        self._publish_status("idle", "control")

    async def start(self, *, task_status: TaskStatus = TASK_STATUS_IGNORED) -> None:
        """Process messages on shell and control channels"""
        async with create_task_group() as tg:
            self.control_stop = threading.Event()
            if not self._is_test and self.control_socket is not None:
                if self.control_thread:
                    self.control_thread.set_task(self.control_main)
                    self.control_thread.start()
                else:
                    tg.start_soon(self.control_main)

            self.shell_interrupt: queue.Queue[bool] = queue.Queue()
            self.shell_is_awaiting = False
            self.shell_is_blocking = False
            self.shell_stop = threading.Event()
            if not self._is_test and self.shell_socket is not None:
                tg.start_soon(self.shell_main)

        if self.shell_stream:
            self.shell_stream.on_recv(
                partial(
                    self.schedule_dispatch,
                    self.dispatch_shell,
                ),
                copy=False,
            )

    def stop(self):
        self.shell_stop.set()
        self.control_stop.set()

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
        socket,
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
            socket,
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

    async def execute_request(self, socket, ident, parent):
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

        # Call do_execute with the appropriate arguments
        reply_content = self.do_execute(**do_execute_args)

        if inspect.isawaitable(reply_content):
            reply_content = await reply_content

        # Flush output before sending the reply.
        sys.stdout.flush()
        sys.stderr.flush()
        # FIXME: on rare occasions, the flush doesn't seem to make it to the
        # clients... This seems to mitigate the problem, but we definitely need
        # to better understand what's going on.
        if self._execute_sleep:
            time.sleep(self._execute_sleep)

        # Send the reply.
        reply_content = json_clean(reply_content)
        metadata = self.finish_metadata(parent, metadata, reply_content)

        reply_msg = self.session.send(
            socket,
            "execute_reply",
            reply_content,
            parent,
            metadata=metadata,
            ident=ident,
        )

        self.log.debug("%s", reply_msg)

        assert reply_msg is not None
        if not silent and reply_msg["content"]["status"] == "error" and stop_on_error:
            # while this flag is true,
            # execute requests will be aborted
            self._aborting = True
            self._aborted_time = time.monotonic()
            self.log.info("Aborting queue")

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

    async def complete_request(self, socket, ident, parent):
        """Handle a completion request."""
        if not self.session:
            return
        content = parent["content"]
        code = content["code"]
        cursor_pos = content["cursor_pos"]

        matches = self.do_complete(code, cursor_pos)
        if inspect.isawaitable(matches):
            matches = await matches

        matches = json_clean(matches)
        self.session.send(socket, "complete_reply", matches, parent, ident)

    def do_complete(self, code, cursor_pos):
        """Override in subclasses to find completions."""
        return {
            "matches": [],
            "cursor_end": cursor_pos,
            "cursor_start": cursor_pos,
            "metadata": {},
            "status": "ok",
        }

    async def inspect_request(self, socket, ident, parent):
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

        # Before we send this object over, we scrub it for JSON usage
        reply_content = json_clean(reply_content)
        msg = self.session.send(socket, "inspect_reply", reply_content, parent, ident)
        self.log.debug("%s", msg)

    def do_inspect(self, code, cursor_pos, detail_level=0, omit_sections=()):
        """Override in subclasses to allow introspection."""
        return {"status": "ok", "data": {}, "metadata": {}, "found": False}

    async def history_request(self, socket, ident, parent):
        """Handle a history request."""
        if not self.session:
            return
        content = parent["content"]

        reply_content = self.do_history(**content)
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content

        reply_content = json_clean(reply_content)
        msg = self.session.send(socket, "history_reply", reply_content, parent, ident)
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

    async def connect_request(self, socket, ident, parent):
        """Handle a connect request."""
        if not self.session:
            return
        content = self._recorded_ports.copy() if self._recorded_ports else {}
        content["status"] = "ok"
        msg = self.session.send(socket, "connect_reply", content, parent, ident)
        self.log.debug("%s", msg)

    @property
    def kernel_info(self):
        return {
            "protocol_version": kernel_protocol_version,
            "implementation": self.implementation,
            "implementation_version": self.implementation_version,
            "language_info": self.language_info,
            "banner": self.banner,
            "help_links": self.help_links,
        }

    async def kernel_info_request(self, socket, ident, parent):
        """Handle a kernel info request."""
        if not self.session:
            return
        content = {"status": "ok"}
        content.update(self.kernel_info)
        msg = self.session.send(socket, "kernel_info_reply", content, parent, ident)
        self.log.debug("%s", msg)

    async def comm_info_request(self, socket, ident, parent):
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
        msg = self.session.send(socket, "comm_info_reply", reply_content, parent, ident)
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

    async def interrupt_request(self, socket, ident, parent):
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

        self.session.send(socket, "interrupt_reply", content, parent, ident=ident)
        return

    async def shutdown_request(self, socket, ident, parent):
        """Handle a shutdown request."""
        if not self.session:
            return
        content = self.do_shutdown(parent["content"]["restart"])
        if inspect.isawaitable(content):
            content = await content
        self.session.send(socket, "shutdown_reply", content, parent, ident=ident)
        # same content, but different msg_id for broadcasting on IOPub
        self._shutdown_message = self.session.msg("shutdown_reply", content, parent)

        await self._at_shutdown()

        self.stop()

    def do_shutdown(self, restart):
        """Override in subclasses to do things when the frontend shuts down the
        kernel.
        """
        return {"status": "ok", "restart": restart}

    async def is_complete_request(self, socket, ident, parent):
        """Handle an is_complete request."""
        if not self.session:
            return
        content = parent["content"]
        code = content["code"]

        reply_content = self.do_is_complete(code)
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
        reply_content = json_clean(reply_content)
        reply_msg = self.session.send(socket, "is_complete_reply", reply_content, parent, ident)
        self.log.debug("%s", reply_msg)

    def do_is_complete(self, code):
        """Override in subclasses to find completions."""
        return {"status": "unknown"}

    async def debug_request(self, socket, ident, parent):
        """Handle a debug request."""
        if not self.session:
            return
        content = parent["content"]
        reply_content = self.do_debug_request(content)
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
        reply_content = json_clean(reply_content)
        reply_msg = self.session.send(socket, "debug_reply", reply_content, parent, ident)
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

    async def usage_request(self, socket, ident, parent):
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
        reply_msg = self.session.send(socket, "usage_reply", reply_content, parent, ident)
        self.log.debug("%s", reply_msg)

    async def do_debug_request(self, msg):
        raise NotImplementedError

    # ---------------------------------------------------------------------------
    # Engine methods (DEPRECATED)
    # ---------------------------------------------------------------------------

    async def apply_request(self, socket, ident, parent):  # pragma: no cover
        """Handle an apply request."""
        self.log.warning("apply_request is deprecated in kernel_base, moving to ipyparallel.")
        try:
            content = parent["content"]
            bufs = parent["buffers"]
            msg_id = parent["header"]["msg_id"]
        except Exception:
            self.log.error("Got bad msg: %s", parent, exc_info=True)  # noqa: G201
            return

        md = self.init_metadata(parent)

        reply_content, result_buf = self.do_apply(content, bufs, msg_id, md)

        # flush i/o
        sys.stdout.flush()
        sys.stderr.flush()

        md = self.finish_metadata(parent, md, reply_content)
        if not self.session:
            return
        self.session.send(
            socket,
            "apply_reply",
            reply_content,
            parent=parent,
            ident=ident,
            buffers=result_buf,
            metadata=md,
        )

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        """DEPRECATED"""
        raise NotImplementedError

    # ---------------------------------------------------------------------------
    # Control messages (DEPRECATED)
    # ---------------------------------------------------------------------------

    async def abort_request(self, socket, ident, parent):  # pragma: no cover
        """abort a specific msg by id"""
        self.log.warning(
            "abort_request is deprecated in kernel_base. It is only part of IPython parallel"
        )
        msg_ids = parent["content"].get("msg_ids", None)
        if isinstance(msg_ids, str):
            msg_ids = [msg_ids]
        for mid in msg_ids:
            self.aborted.add(str(mid))

        content = dict(status="ok")
        if not self.session:
            return
        reply_msg = self.session.send(
            socket, "abort_reply", content=content, parent=parent, ident=ident
        )
        self.log.debug("%s", reply_msg)

    async def clear_request(self, socket, idents, parent):  # pragma: no cover
        """Clear our namespace."""
        self.log.warning(
            "clear_request is deprecated in kernel_base. It is only part of IPython parallel"
        )
        content = self.do_clear()
        if self.session:
            self.session.send(socket, "clear_reply", ident=idents, parent=parent, content=content)

    def do_clear(self):
        """DEPRECATED since 4.0.3"""
        raise NotImplementedError

    # ---------------------------------------------------------------------------
    # Protected interface
    # ---------------------------------------------------------------------------

    def _topic(self, topic):
        """prefixed topic for IOPub messages"""
        base = "kernel.%s" % self.ident

        return (f"{base}.{topic}").encode()

    _aborting = Bool(False)

    def _abort_queues(self):
        # while this flag is true,
        # execute requests will be aborted
        self._aborting = True
        self.log.info("Aborting queue")

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

    async def _send_abort_reply(self, socket, msg, idents):
        """Send a reply to an aborted request"""
        if not self.session:
            return
        self.log.info("Aborting %s: %s", msg["header"]["msg_id"], msg["header"]["msg_type"])
        reply_type = msg["header"]["msg_type"].rsplit("_", 1)[0] + "_reply"
        status = {"status": "aborted"}
        md = self.init_metadata(msg)
        md = self.finish_metadata(msg, md, status)
        md.update(status)

        assert self.session is not None
        self.session.send(
            socket,
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
        sys.stderr.flush()
        sys.stdout.flush()

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
