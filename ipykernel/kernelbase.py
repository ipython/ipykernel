"""Base class for a kernel that talks to frontends over 0MQ."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio
import inspect
import itertools
import logging
import os
import sys
import threading
import time
import typing as t
import uuid
import warnings
from datetime import datetime
from signal import SIGINT, SIGTERM, Signals

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

import janus
import psutil
import zmq
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
from .shell import ShellThread


def DEBUG(msg):
    with open("debug.log", "a") as f:
        f.write(f"{msg}\n")


def _accepts_arg(meth, arg: str):
    parameters = inspect.signature(meth).parameters
    cid_param = parameters.get(arg)
    return (cid_param and cid_param.kind == cid_param.KEYWORD_ONLY) or any(
        p.kind == p.VAR_KEYWORD for p in parameters.values()
    )


class Kernel(SingletonConfigurable):
    """The base kernel class."""

    # ---------------------------------------------------------------------------
    # Kernel interface
    # ---------------------------------------------------------------------------

    # attribute to override with a GUI
    eventloop = Any(None)

    processes: t.Dict[str, psutil.Process] = {}

    @observe("eventloop")
    def _update_eventloop(self, change):
        """schedule call to eventloop from IOLoop"""
        loop = asyncio.get_running_loop()
        if change.new is not None:
            loop.call_soon(self.enter_eventloop)

    session = Instance(Session, allow_none=True)
    profile_dir = Instance("IPython.core.profiledir.ProfileDir", allow_none=True)
    shell_socket = Instance(zmq.asyncio.Socket, allow_none=True)

    implementation: str
    implementation_version: str
    banner: str

    control_socket = Instance(zmq.asyncio.Socket, allow_none=True)

    debug_shell_socket = Any()

    shell_msg_thread = Any()
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
    language_info: t.Dict[str, object] = {}

    # any links that should go in the help menu
    help_links = List()

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
    _parents = Dict({"shell": {}, "control": {}})
    _parent_ident = Dict({"shell": b"", "control": b""})

    @property
    def _parent_header(self):
        warnings.warn(
            "Kernel._parent_header is deprecated in ipykernel 6. Use .get_parent()",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_parent(channel="shell")

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
    control_msg_types = msg_types + [
        "clear_request",
        "abort_request",
        "debug_request",
        "usage_request",
        "create_subshell_request",
    ]

    def __init__(self, **kwargs):
        """Initialize the kernel."""
        super().__init__(**kwargs)
        self.shell_socket_lock = threading.Lock()
        self.shells = {None: {}}
        # Build dict of handlers for message types
        self.shell_handlers = {}
        for msg_type in self.msg_types:
            self.shell_handlers[msg_type] = getattr(self, msg_type)

        self.control_handlers = {}
        for msg_type in self.control_msg_types:
            self.control_handlers[msg_type] = getattr(self, msg_type)

    async def should_handle(self, socket, msg, idents):
        """Check whether a shell-channel message should be handled

        Allows subclasses to prevent handling of certain messages (e.g. aborted requests).
        """
        msg_id = msg["header"]["msg_id"]
        if msg_id in self.aborted:
            # is it safe to assume a msg_id will not be resubmitted?
            self.aborted.remove(msg_id)
            await self._send_abort_reply(socket, msg, idents)
            return False
        return True

    def pre_handler_hook(self):
        """Hook to execute before calling message handler"""
        # ensure default_int_handler during handler call
        # self.saved_sigint_handler = signal(SIGINT, default_int_handler)
        pass

    def post_handler_hook(self):
        """Hook to execute after calling message handler"""
        # signal(SIGINT, self.saved_sigint_handler)
        pass

    def enter_eventloop(self):
        """enter eventloop"""
        self.log.info("Entering eventloop %s", self.eventloop)
        # record handle, so we can check when this changes
        eventloop = self.eventloop
        if eventloop is None:
            self.log.info("Exiting as there is no eventloop")
            return

        def advance_eventloop():
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
                pass
            if self.eventloop is eventloop:
                # schedule advance again
                schedule_next()

        def schedule_next():
            """Schedule the next advance of the eventloop"""
            # flush the eventloop every so often,
            # giving us a chance to handle messages in the meantime
            self.log.debug("Scheduling eventloop advance")
            asyncio.get_running_loop().call_later(0.001, advance_eventloop)

        # begin polling the eventloop
        schedule_next()

    _message_counter = Any(
        help="""Monotonic counter of messages
        """,
    )

    @default("_message_counter")
    def _message_counter_default(self):
        return itertools.count()

    async def get_shell_messages(self):
        """Get messages from the shell socket, in a separate thread if sub-shells are supported,
        in the main thread otherwise.
        """
        while True:
            await self.get_shell_message()

    async def get_shell_message(self, msg=None):
        """Get a message from the shell socket, in a separate thread if sub-shells are supported,
        in the main thread otherwise.

        Allow by-passing the socket and injecting a message for testing.
        """
        msg = msg or await self.shell_socket.recv_multipart()
        idents, msg = self.session.feed_identities(msg, copy=True)
        try:
            msg = self.session.deserialize(msg, content=True, copy=True)
        except BaseException:
            self.log.error("Invalid Message", exc_info=True)
            return

        shell_id = msg["header"].get("shell_id")
        # the shell message queue for this sub-shell might not have been created yet,
        # because done in another thread, it should be ok to not use a lock here
        while shell_id not in self.shells or "messages" not in self.shells[shell_id]:
            await asyncio.sleep(0.1)
        if self.shell_msg_thread:
            self.shells[shell_id]["messages"].sync_q.put((idents, msg))
        else:
            self.shells[shell_id]["messages"].put_nowait((idents, msg))

    async def process_shell_messages(self, shell_id=None):
        # create a message queue only for sub-shells (already created for main shell)
        if shell_id is not None:
            lib = janus if self.shell_msg_thread else asyncio
            self.shells[shell_id]["interrupt"] = lib.Queue()
            self.shells[shell_id]["messages"] = lib.Queue()
        while True:
            if self.shell_msg_thread:
                idents, msg = await self.shells[shell_id]["messages"].async_q.get()
            else:
                idents, msg = await self.shells[shell_id]["messages"].get()

            # Set the parent message for side effects.
            self.set_parent(idents, msg, channel="shell")
            self._publish_status("busy", "shell")

            msg_type = msg["header"]["msg_type"]

            # Only abort execute requests
            if self._aborting and msg_type == "execute_request":
                await self._send_abort_reply(self.shell_socket, msg, idents)
                self._publish_status("idle", "shell")
                # flush to ensure reply is sent before
                # handling the next request
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
                        DEBUG(f"{shell_id} {result=}")
                except Exception:
                    self.log.error("Exception in message handler:", exc_info=True)
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
            # flush to ensure reply is sent before
            # handling the next request

    async def process_control_messages(self):
        while True:
            msg = await self.control_socket.recv_multipart()
            idents, msg = self.session.feed_identities(msg, copy=True)
            try:
                msg = self.session.deserialize(msg, content=True, copy=True)
            except Exception:
                self.log.error("Invalid Control Message", exc_info=True)
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
                    result = handler(self.control_socket, idents, msg)
                    if inspect.isawaitable(result):
                        await result
                except Exception:
                    self.log.error("Exception in control handler:", exc_info=True)

            sys.stdout.flush()
            sys.stderr.flush()
            self._publish_status("idle", "control")
            # flush to ensure reply is sent

    def start(self):
        """Process messages on shell and control channels"""
        self.exec_done = asyncio.Event()
        self.io_loop = asyncio.get_running_loop()

        if self.control_thread:
            self.control_thread.create_task(self.process_control_messages())
        else:
            asyncio.create_task(self.process_control_messages())

        self.shells[None]["interrupt"] = asyncio.Queue()
        self.shells[None]["thread"] = None
        if self.shell_msg_thread:
            self.shells[None]["messages"] = janus.Queue()
            self.shell_msg_thread.create_task(self.get_shell_messages())
        else:
            # if sub-shells are not supported, getting messages and processing them is done in the main thread
            # so use an asyncio.Queue directly, no need to handle multi-threading
            self.shells[None]["messages"] = asyncio.Queue()
            asyncio.create_task(self.get_shell_messages())

        asyncio.create_task(self.process_shell_messages())  # main shell/thread

        # publish idle status
        self._publish_status("starting", "shell")

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

        self.session.send(
            self.iopub_socket,
            "execute_input",
            {"code": code, "execution_count": execution_count},
            parent=parent,
            ident=self._topic("execute_input"),
        )

    def _publish_status(self, status, channel, parent=None):
        """send status (busy/idle) on IOPub"""
        self.session.send(
            self.iopub_socket,
            "status",
            {"execution_state": status},
            parent=parent or self.get_parent(channel),
            ident=self._topic("status"),
        )

    def _publish_debug_event(self, event):
        self.session.send(
            self.iopub_socket,
            "debug_event",
            event,
            parent=self.get_parent("control"),
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

    def get_parent(self, channel="shell"):
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
        channel="shell",
    ):
        """Send a response to the message we're currently processing.

        This accepts all the parameters of :meth:`jupyter_client.session.Session.send`
        except ``parent``.

        This relies on :meth:`set_parent` having been called for the current
        message.
        """
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

    async def execute_request(self, socket, ident, parent):
        """handle an execute_request"""
        try:
            content = parent["content"]
            code = content["code"]
            silent = content["silent"]
            store_history = content.get("store_history", not silent)
            user_expressions = content.get("user_expressions", {})
            allow_stdin = content.get("allow_stdin", False)
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

        shell_id = parent["header"].get("shell_id")
        cell_id = parent.get("metadata", {}).get("cellId")

        kwargs = dict()
        if _accepts_arg(self.do_execute, "shell_id"):
            kwargs.update(shell_id=shell_id)
        if _accepts_arg(self.do_execute, "cell_id"):
            kwargs.update(cell_id=cell_id)

        reply_content = self.do_execute(
            code, silent, store_history, user_expressions, allow_stdin, **kwargs
        )
        DEBUG(f"execute_request {parent['header'].get('shell_id')}")

        if inspect.isawaitable(reply_content):
            reply_content = await reply_content
            DEBUG(f"{parent['header'].get('shell_id')} {reply_content=}")

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

        DEBUG(f"sending reply for shell_id: {parent['header'].get('shell_id')}")
        with self.shell_socket_lock:
            reply_msg = self.session.send(
                socket,
                "execute_reply",
                reply_content,
                parent,
                metadata=metadata,
                ident=ident,
            )

        self.log.debug("%s", reply_msg)

        if not silent and reply_msg["content"]["status"] == "error" and stop_on_error:
            await self._abort_queues()

    def do_execute(
        self,
        code,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=False,
        *,
        cell_id=None,
        shell_id=None,
    ):
        """Execute user code. Must be overridden by subclasses."""
        raise NotImplementedError

    async def complete_request(self, stream, ident, parent):
        """Handle a completion request."""
        content = parent["content"]
        code = content["code"]
        cursor_pos = content["cursor_pos"]

        matches = self.do_complete(code, cursor_pos)
        if inspect.isawaitable(matches):
            matches = await matches

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
        msg = self.session.send(stream, "inspect_reply", reply_content, parent, ident)
        self.log.debug("%s", msg)

    def do_inspect(self, code, cursor_pos, detail_level=0, omit_sections=()):
        """Override in subclasses to allow introspection."""
        return {"status": "ok", "data": {}, "metadata": {}, "found": False}

    async def history_request(self, stream, ident, parent):
        """Handle a history request."""
        content = parent["content"]

        reply_content = self.do_history(**content)
        if inspect.isawaitable(reply_content):
            reply_content = await reply_content

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
        if self._recorded_ports is not None:
            content = self._recorded_ports.copy()
        else:
            content = {}
        content["status"] = "ok"
        msg = self.session.send(stream, "connect_reply", content, parent, ident)
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

    async def create_subshell_request(self, socket, ident, parent):
        shell_id = str(uuid.uuid4())
        self.shells[shell_id] = {}
        self.shells[shell_id]["thread"] = subshell_thread = ShellThread(shell_id)
        subshell_thread.start()
        subshell_thread.create_task(self.process_shell_messages(shell_id))
        content = {
            "status": "ok",
            "shell_id": shell_id,
        }
        self.session.send(socket, "create_subshell_reply", content, parent, ident)

    async def kernel_info_request(self, socket, ident, parent):
        """Handle a kernel info request."""
        content = {"status": "ok"}
        content.update(self.kernel_info)
        msg = self.session.send(socket, "kernel_info_reply", content, parent, ident)
        self.log.debug("%s", msg)

    async def comm_info_request(self, stream, ident, parent):
        """Handle a comm info request."""
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

    def _send_interupt_children(self):
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
                    return
                except OSError:
                    pass
            try:
                os.kill(pid, SIGINT)
            except OSError:
                pass

    async def interrupt_request(self, socket, ident, parent):
        """Handle an interrupt request."""
        self._send_interupt_children()
        content = parent["content"]
        self.session.send(socket, "interrupt_reply", content, parent, ident=ident)
        return

    async def shutdown_request(self, socket, ident, parent):
        """Handle a shutdown request."""
        content = self.do_shutdown(parent["content"]["restart"])
        if inspect.isawaitable(content):
            content = await content
        self.session.send(socket, "shutdown_reply", content, parent, ident=ident)
        # same content, but different msg_id for broadcasting on IOPub
        self._shutdown_message = self.session.msg("shutdown_reply", content, parent)

        await self._at_shutdown()

        if self.control_thread:
            self.control_thread.stop()
        if self.shell_msg_thread:
            self.shell_msg_thread.stop()
        if self.iopub_thread:
            self.iopub_thread.stop()
        for shell in self.shells.values():
            subshell_thread = shell["thread"]
            if subshell_thread is not None:
                subshell_thread.stop()

        self._stop_queue.sync_q.put(None)

    def do_shutdown(self, restart):
        """Override in subclasses to do things when the frontend shuts down the
        kernel.
        """
        return {"status": "ok", "restart": restart}

    async def is_complete_request(self, socket, ident, parent):
        """Handle an is_complete request."""
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
            else:  # ... or a number
                return metric_value
        # Avoid littering logs with stack traces
        # complaining about dead processes
        except BaseException:
            return None

    async def usage_request(self, socket, ident, parent):
        """Handle a usage request."""
        reply_content = {"hostname": socket.gethostname(), "pid": os.getpid()}
        current_process = psutil.Process()
        all_processes = [current_process] + current_process.children(recursive=True)
        # Ensure 1) self.processes is updated to only current subprocesses
        # and 2) we reuse processes when possible (needed for accurate CPU)
        self.processes = {
            process.pid: self.processes.get(process.pid, process) for process in all_processes
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
        if cpu_percent is not None and cpu_percent != 0.0:
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
            self.log.error("Got bad msg: %s", parent, exc_info=True)
            return

        md = self.init_metadata(parent)

        reply_content, result_buf = self.do_apply(content, bufs, msg_id, md)

        # flush i/o
        sys.stdout.flush()
        sys.stderr.flush()

        md = self.finish_metadata(parent, md, reply_content)

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
        if not msg_ids:
            await self._abort_queues()
        for mid in msg_ids:
            self.aborted.add(str(mid))

        content = dict(status="ok")
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

    async def _abort_queues(self):
        # while this flag is true,
        # execute requests will be aborted
        self._aborting = True
        self.log.info("Aborting queue")

        # flush streams, so all currently waiting messages
        # are added to the queue

        # Callback to signal that we are done aborting
        # dispatch functions _must_ be async
        async def stop_aborting():
            await asyncio.sleep(self.stop_on_error_timeout)
            self.log.info("Finishing abort")
            self._aborting = False

        # put the stop-aborting event on the message queue
        # so that all messages already waiting in the queue are aborted
        # before we reset the flag
        # schedule_stop_aborting = partial(self.schedule_dispatch, stop_aborting)

        # if we have a delay, give messages this long to arrive on the queue
        # before we stop aborting requests
        # asyncio.get_event_loop().call_later(self.stop_on_error_timeout, schedule_stop_aborting)
        asyncio.create_task(stop_aborting())

    async def _send_abort_reply(self, socket, msg, idents):
        """Send a reply to an aborted request"""
        self.log.info(f"Aborting {msg['header']['msg_id']}: {msg['header']['msg_type']}")
        reply_type = msg["header"]["msg_type"].rsplit("_", 1)[0] + "_reply"
        status = {"status": "aborted"}
        md = self.init_metadata(msg)
        md = self.finish_metadata(msg, md, status)
        md.update(status)

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
        raise StdinNotImplementedError(
            "raw_input was called, but this frontend does not support stdin."
        )

    def getpass(self, prompt="", stream=None):
        """Forward getpass to frontends

        Raises
        ------
        StdinNotImplementedError if active frontend doesn't support stdin.
        """
        if not self._allow_stdin:
            raise StdinNotImplementedError(
                "getpass was called, but this frontend does not support input requests."
            )
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
            raise StdinNotImplementedError(
                "raw_input was called, but this frontend does not support input requests."
            )
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
                else:
                    raise

        # Send the input request.
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
                raise KeyboardInterrupt("Interrupted by user") from None
            except Exception:
                self.log.warning("Invalid Message:", exc_info=True)

        try:
            value = reply["content"]["value"]
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
        for p in self._process_children():
            self.log.debug(f"Sending {Signals(signum)!r} to subprocess {p}")
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
                    f"Will sleep {delay}s before checking for children and retrying. {children}"
                )
                await asyncio.sleep(delay)

    async def _at_shutdown(self):
        """Actions taken at shutdown by the kernel, called by python's atexit."""
        try:
            await self._progressively_terminate_all_children()
        except Exception as e:
            self.log.exception("Exception during subprocesses termination %s", e)

        finally:
            if self._shutdown_message is not None:
                self.session.send(
                    self.iopub_socket,
                    self._shutdown_message,
                    ident=self._topic("shutdown"),
                )
                self.log.debug("%s", self._shutdown_message)
