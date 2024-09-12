"""Manager of subshells in a kernel."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import typing as t
import uuid
from dataclasses import dataclass
from threading import Lock, current_thread, main_thread

import zmq
import zmq.asyncio
from anyio import Event, create_task_group

from .subshell import SubshellThread


@dataclass
class Subshell:
    thread: SubshellThread
    shell_channel_socket: zmq.asyncio.Socket


class SubshellManager:
    """A manager of subshells.

    Controls the lifetimes of subshell threads and their associated ZMQ sockets.
    Runs mostly in the shell channel thread.

    Care needed with threadsafe access here.  All write access to the cache occurs in
    the shell channel thread so there is only ever one write access at any one time.
    Reading of cache information can be performed by other threads, so all reads are
    protected by a lock so that they are atomic.
    """

    def __init__(self, context: zmq.asyncio.Context, shell_socket):
        assert current_thread() == main_thread()

        self._context: zmq.asyncio.Context = context
        self._shell_socket = shell_socket
        self._cache: dict[str, Subshell] = {}
        self._lock: Lock = Lock()

        # Inproc pair sockets for control channel and main shell (parent subshell).
        # Each inproc pair has a "shell_channel" socket used in the shell channel
        # thread, and an "other" socket used in the other thread.
        self._control_shell_channel_socket = self._create_inproc_pair_socket("control", True)
        self._control_other_socket = self._create_inproc_pair_socket("control", False)
        self._parent_shell_channel_socket = self._create_inproc_pair_socket(None, True)
        self._parent_other_socket = self._create_inproc_pair_socket(None, False)

        self._poller = zmq.asyncio.Poller()
        self._poller.register(self._parent_shell_channel_socket, zmq.POLLIN)
        self._subshell_change = Event()

    def close(self):
        """Stop all subshells and close all resources."""
        assert current_thread().name == "Shell channel"

        for socket in (
            self._control_shell_channel_socket,
            self._control_other_socket,
            self._parent_shell_channel_socket,
            self._parent_other_socket,
        ):
            if socket is not None:
                socket.close()

        with self._lock:
            while True:
                try:
                    _, subshell = self._cache.popitem()
                except KeyError:
                    break
                self._stop_subshell(subshell)

    def get_control_other_socket(self):
        return self._control_other_socket

    def get_other_socket(self, subshell_id: str | None):
        """Return the other inproc pair socket for a subshell.

        This socket is accessed from the subshell thread.
        """
        if subshell_id is None:
            return self._parent_other_socket
        with self._lock:
            return self._cache[subshell_id].thread._pair_socket

    def get_shell_channel_socket(self, subshell_id: str | None):
        """Return the shell channel inproc pair socket for a subshell.

        This socket is accessed from the shell channel thread.
        """
        if subshell_id is None:
            return self._parent_shell_channel_socket
        with self._lock:
            return self._cache[subshell_id].shell_channel_socket

    def list_subshell(self) -> list[str]:
        """Return list of current subshell ids.

        Can be called by any subshell using %subshell magic.
        """
        with self._lock:
            return list(self._cache)

    async def listen_from_control(self, subshell_task):
        """Listen for messages on the control inproc socket, handle those messages and
        return replies on the same socket.  Runs in the shell channel thread.
        """
        assert current_thread().name == "Shell channel"

        socket = self._control_shell_channel_socket
        while True:
            request = await socket.recv_json()
            reply = await self._process_control_request(request, subshell_task)
            await socket.send_json(reply)

    async def listen_from_subshells(self):
        """Listen for reply messages on inproc sockets of all subshells and resend
        those messages to the client via the shell_socket.

        Runs in the shell channel thread.
        """
        assert current_thread().name == "Shell channel"

        while True:
            async with create_task_group() as tg:
                tg.start_soon(self._listen_from_subshells)
                await self._subshell_change.wait()
                tg.cancel_scope.cancel()

            # anyio.Event is single use, so recreate to reuse
            self._subshell_change = Event()

    def subshell_id_from_thread_id(self, thread_id) -> str | None:
        """Return subshell_id of the specified thread_id.

        Raises RuntimeError if thread_id is not the main shell or a subshell.

        Only used by %subshell magic so does not have to be fast/cached.
        """
        with self._lock:
            if thread_id == main_thread().ident:
                return None
            for id, subshell in self._cache.items():
                if subshell.thread.ident == thread_id:
                    return id
            msg = f"Thread id '{thread_id} does not correspond to a subshell of this kernel"
            raise RuntimeError(msg)

    def _create_inproc_pair_socket(self, name: str | None, shell_channel_end: bool):
        """Create and return a single ZMQ inproc pair socket."""
        address = self._get_inproc_socket_address(name)
        socket = self._context.socket(zmq.PAIR)
        if shell_channel_end:
            socket.bind(address)
        else:
            socket.connect(address)
        return socket

    async def _create_subshell(self, subshell_task) -> str:
        """Create and start a new subshell thread."""
        assert current_thread().name == "Shell channel"

        subshell_id = str(uuid.uuid4())
        thread = SubshellThread(subshell_id)

        with self._lock:
            assert subshell_id not in self._cache
            shell_channel_socket = self._create_inproc_pair_socket(subshell_id, True)
            self._cache[subshell_id] = Subshell(thread, shell_channel_socket)

        address = self._get_inproc_socket_address(subshell_id)
        thread.add_task(thread.create_pair_socket, self._context, address)
        thread.add_task(subshell_task, subshell_id)
        thread.start()

        self._poller.register(shell_channel_socket, zmq.POLLIN)
        self._subshell_change.set()

        return subshell_id

    def _delete_subshell(self, subshell_id: str) -> None:
        """Delete subshell identified by subshell_id.

        Raises key error if subshell_id not in cache.
        """
        assert current_thread().name == "Shell channel"

        with self._lock:
            subshell = self._cache.pop(subshell_id)

        self._stop_subshell(subshell)

    def _get_inproc_socket_address(self, name: str | None):
        full_name = f"subshell-{name}" if name else "subshell"
        return f"inproc://{full_name}"

    async def _listen_from_subshells(self):
        """Await next reply message from any subshell (parent or child) and resend
        to the client via the shell_socket.

        If a subshell is created or deleted then the poller is updated and the task
        executing this function is cancelled and then rescheduled with the updated
        poller.

        Runs in the shell channel thread.
        """
        assert current_thread().name == "Shell channel"

        while True:
            for socket, _ in await self._poller.poll():
                msg = await socket.recv_multipart(copy=False)
                self._shell_socket.send_multipart(msg)

    async def _process_control_request(self, request, subshell_task):
        """Process a control request message received on the control inproc
        socket and return the reply.  Runs in the shell channel thread.
        """
        assert current_thread().name == "Shell channel"

        try:
            type = request["type"]
            reply: dict[str, t.Any] = {"status": "ok"}

            if type == "create":
                reply["subshell_id"] = await self._create_subshell(subshell_task)
            elif type == "delete":
                subshell_id = request["subshell_id"]
                self._delete_subshell(subshell_id)
            elif type == "list":
                reply["subshell_id"] = self.list_subshell()
            else:
                msg = f"Unrecognised message type {type}"
                raise RuntimeError(msg)
        except BaseException as err:
            reply = {
                "status": "error",
                "evalue": str(err),
            }
        return reply

    def _stop_subshell(self, subshell: Subshell):
        """Stop a subshell thread and close all of its resources."""
        assert current_thread().name == "Shell channel"

        thread = subshell.thread
        if thread.is_alive():
            thread.stop()
            thread.join()

        self._poller.unregister(subshell.shell_channel_socket)
        self._subshell_change.set()
        subshell.shell_channel_socket.close()
