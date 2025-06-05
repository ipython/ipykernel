"""Manager of subshells in a kernel."""
from __future__ import annotations

import json
import typing as t
import uuid
from functools import partial
from threading import Lock, current_thread, main_thread

import zmq
from tornado.ioloop import IOLoop

from .socket_pair import SocketPair
from .subshell import SubshellThread
from .thread import SHELL_CHANNEL_THREAD_NAME


class SubshellManager:
    """A manager of subshells.

    Controls the lifetimes of subshell threads and their associated ZMQ sockets and
    streams. Runs mostly in the shell channel thread.

    Care needed with threadsafe access here.  All write access to the cache occurs in
    the shell channel thread so there is only ever one write access at any one time.
    Reading of cache information can be performed by other threads, so all reads are
    protected by a lock so that they are atomic.

    Sending reply messages via the shell_socket is wrapped by another lock to protect
    against multiple subshells attempting to send at the same time.
    """

    def __init__(
        self,
        context: zmq.Context[t.Any],
        shell_channel_io_loop: IOLoop,
        shell_socket: zmq.Socket[t.Any],
    ):
        assert current_thread() == main_thread()

        self._context: zmq.Context[t.Any] = context
        self._shell_channel_io_loop = shell_channel_io_loop
        self._shell_socket = shell_socket
        self._cache: dict[str, SubshellThread] = {}
        self._lock_cache = Lock()
        self._lock_shell_socket = Lock()

        # Inproc socket pair for communication from control thread to shell channel thread,
        # such as for create_subshell_request messages. Reply messages are returned straight away.
        self.control_to_shell_channel = SocketPair(self._context, "control")
        self.control_to_shell_channel.on_recv(
            self._shell_channel_io_loop, self._process_control_request, copy=True
        )

        # Inproc socket pair for communication from shell channel thread to main thread,
        # such as for execute_request messages.
        self._shell_channel_to_main = SocketPair(self._context, "main")

        # Inproc socket pair for communication from main thread to shell channel thread.
        # such as for execute_reply messages.
        self._main_to_shell_channel = SocketPair(self._context, "main-reverse")
        self._main_to_shell_channel.on_recv(
            self._shell_channel_io_loop, self._send_on_shell_channel
        )

    def close(self) -> None:
        """Stop all subshells and close all resources."""
        assert current_thread().name == SHELL_CHANNEL_THREAD_NAME
        with self._lock_cache:
            while True:
                try:
                    _, subshell_thread = self._cache.popitem()
                except KeyError:
                    break
                self._stop_subshell(subshell_thread)

        self.control_to_shell_channel.close()
        self._main_to_shell_channel.close()
        self._shell_channel_to_main.close()

    def get_shell_channel_to_subshell_pair(self, subshell_id: str | None) -> SocketPair:
        if subshell_id is None:
            return self._shell_channel_to_main
        with self._lock_cache:
            return self._cache[subshell_id].shell_channel_to_subshell

    def get_subshell_to_shell_channel_socket(self, subshell_id: str | None) -> zmq.Socket[t.Any]:
        if subshell_id is None:
            return self._main_to_shell_channel.from_socket
        with self._lock_cache:
            return self._cache[subshell_id].subshell_to_shell_channel.from_socket

    def get_shell_channel_to_subshell_socket(self, subshell_id: str | None) -> zmq.Socket[t.Any]:
        return self.get_shell_channel_to_subshell_pair(subshell_id).from_socket

    def get_subshell_aborting(self, subshell_id: str) -> bool:
        """Get the aborting flag of the specified subshell."""
        return self._cache[subshell_id].aborting

    def list_subshell(self) -> list[str]:
        """Return list of current subshell ids.

        Can be called by any subshell using %subshell magic.
        """
        with self._lock_cache:
            return list(self._cache)

    def set_on_recv_callback(self, on_recv_callback):
        assert current_thread() == main_thread()
        self._on_recv_callback = on_recv_callback
        self._shell_channel_to_main.on_recv(IOLoop.current(), partial(self._on_recv_callback, None))

    def set_subshell_aborting(self, subshell_id: str, aborting: bool) -> None:
        """Set the aborting flag of the specified subshell."""
        with self._lock_cache:
            self._cache[subshell_id].aborting = aborting

    def subshell_id_from_thread_id(self, thread_id: int) -> str | None:
        """Return subshell_id of the specified thread_id.

        Raises RuntimeError if thread_id is not the main shell or a subshell.

        Only used by %subshell magic so does not have to be fast/cached.
        """
        with self._lock_cache:
            if thread_id == main_thread().ident:
                return None
            for id, subshell in self._cache.items():
                if subshell.ident == thread_id:
                    return id
            msg = f"Thread id {thread_id!r} does not correspond to a subshell of this kernel"
            raise RuntimeError(msg)

    def _create_subshell(self) -> str:
        """Create and start a new subshell thread."""
        assert current_thread().name == SHELL_CHANNEL_THREAD_NAME

        subshell_id = str(uuid.uuid4())
        subshell_thread = SubshellThread(subshell_id, self._context)

        with self._lock_cache:
            assert subshell_id not in self._cache
            self._cache[subshell_id] = subshell_thread

        subshell_thread.shell_channel_to_subshell.on_recv(
            subshell_thread.io_loop,
            partial(self._on_recv_callback, subshell_id),
        )

        subshell_thread.subshell_to_shell_channel.on_recv(
            self._shell_channel_io_loop, self._send_on_shell_channel
        )

        subshell_thread.start()
        return subshell_id

    def _delete_subshell(self, subshell_id: str) -> None:
        """Delete subshell identified by subshell_id.

        Raises key error if subshell_id not in cache.
        """
        assert current_thread().name == SHELL_CHANNEL_THREAD_NAME

        with self._lock_cache:
            subshell_threwad = self._cache.pop(subshell_id)

        self._stop_subshell(subshell_threwad)

    def _process_control_request(
        self,
        request: list[t.Any],
    ) -> None:
        """Process a control request message received on the control inproc
        socket and return the reply.  Runs in the shell channel thread.
        """
        assert current_thread().name == SHELL_CHANNEL_THREAD_NAME

        try:
            decoded = json.loads(request[0])
            type = decoded["type"]
            reply: dict[str, t.Any] = {"status": "ok"}

            if type == "create":
                reply["subshell_id"] = self._create_subshell()
            elif type == "delete":
                subshell_id = decoded["subshell_id"]
                self._delete_subshell(subshell_id)
            elif type == "list":
                reply["subshell_id"] = self.list_subshell()
            else:
                msg = f"Unrecognised message type {type!r}"
                raise RuntimeError(msg)
        except BaseException as err:
            reply = {
                "status": "error",
                "evalue": str(err),
            }

        # Return the reply to the control thread.
        self.control_to_shell_channel.to_socket.send_json(reply)

    def _send_on_shell_channel(self, msg) -> None:
        assert current_thread().name == SHELL_CHANNEL_THREAD_NAME
        with self._lock_shell_socket:
            self._shell_socket.send_multipart(msg)

    def _stop_subshell(self, subshell_thread: SubshellThread) -> None:
        """Stop a subshell thread and close all of its resources."""
        assert current_thread().name == SHELL_CHANNEL_THREAD_NAME

        if subshell_thread.is_alive():
            subshell_thread.stop()
            subshell_thread.join()
