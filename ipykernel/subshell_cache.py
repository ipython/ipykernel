"""A cache for subshell information."""
# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from anyio import create_task_group
from dataclasses import dataclass
from threading import Lock, main_thread
import typing as t
import uuid
import zmq

from .subshell import SubshellThread


@dataclass
class Subshell:
    thread: SubshellThread
    send_socket: zmq.Socket
    recv_socket: zmq.Socket



# SubshellManager perhaps???????

class SubshellCache:
    """A cache for subshell information.

    Care needed with threadsafe access here.  After the cache is created, all write
    access is performed by the control thread so there is only ever one write access at
    any one time.  Reading of cache information is performed by a number of different
    threads:

    1) Receive inproc socket for a child subshell is passed to the subshell task (by
       the control thread) when it is created.
    2) Send inproc socket is looked up for every message received by the shell channel
       thread so that the message is sent to the correct subshell thread.
    3) Control thread reads shell_ids for list_subshell_request message.

    Python dictionary reads and writes are atomic and therefore threadsafe because of
    the GIL in conventional CPython.  But wise to use a mutex to support non-GIL
    python.

    Read-only access to the parent subshell sockets never needs to be wrapped in a
    mutex as there is only one pair over the whole lifetime of this object.
    """
    def __init__(self, context: zmq.Context, shell_socket):


        # assert this is only called from the main thread...

        self._context: zmq.Context = context
        self._shell_socket = shell_socket
        self._cache: dict[str, Subshell] = {}
        self._lock: Lock = Lock()

        # Parent subshell sockets.
        self._parent_send_socket, self._parent_recv_socket = \
            self._create_inproc_sockets(None)

        # Socket names are poor. Better to have this/cache end and other end.
        self.control_send_socket, self.control_recv_socket = \
            self._create_inproc_sockets("control")


    def _process_control_request(self, request, subshell_task):
        try:
            type = request["type"]
            reply: dict[str, t.Any] = {"status": "ok"}

            if type == "create":
                reply["subshell_id"] = self.create_subshell(subshell_task)
            elif type == "delete":
                subshell_id = request["subshell_id"]
                self.delete_subshell(subshell_id)
            elif type == "list":
                reply["subshell_id"] = self.list_subshell()
            else:
                raise RuntimeError(f"Unrecognised message type {type}")
        except BaseException as err:
            # Not sure what information to return here.
            reply = {
                "status": "error",
                "evalue": str(err),
            }
        return reply


    async def _TASK(self, subshell_task):  # messages from control channel via inproc pair sockets.
        while True:
            request = await self.control_send_socket.recv_json()
            reply = self._process_control_request(request, subshell_task)
            await self.control_send_socket.send_json(reply)


    async def _from_subshell_task(self, send_socket):
        while True:
            msg = await send_socket.recv_multipart(copy=False)
            with self._lock:
                self._shell_socket.send_multipart(msg)

    async def list_from_control(self):
        async with create_task_group() as tg:
            tg.start_soon(self._TASK)


    def close(self):
        for socket in (self._parent_send_socket, self._parent_recv_socket):
            if socket and not socket.closed:
                socket.close()

        for socket in (self.control_send_socket, self.control_recv_socket):
            if socket and not socket.closed:
                socket.close()

        self._parent_recv_socket = None
        self._parent_send_socket = None
        self.control_send_socket = None
        self.control_recv_socket = None

        with self._lock:
            while True:
                try:
                    _, subshell = self._cache.popitem()
                except KeyError:
                    break
                self._stop_subshell(subshell)

    def create_subshell(self, subshell_task) -> str:
        # Create new subshell thread and start it.

        # check if subshell_id already exists...
        # assume it doesn't so far.

        subshell_id = str(uuid.uuid4())
        thread = SubshellThread(subshell_id)

        with self._lock:
            assert subshell_id not in self._cache
            send_socket, recv_socket = self._create_inproc_sockets(subshell_id)
            self._cache[subshell_id] = Subshell(thread, send_socket, recv_socket)

        thread.add_task(subshell_task, subshell_id)
        thread.add_task(self._from_subshell_task, send_socket)
        thread.start()

        return subshell_id

    def delete_subshell(self, subshell_id: str) -> None:
        """Raises key error if subshell_id not in cache"""
        with self._lock:
            subshell = self._cache.pop(subshell_id)

        self._stop_subshell(subshell)

    def get_recv_socket(self, subshell_id: str | None):
        if subshell_id is None:
            return self._parent_recv_socket
        else:
            with self._lock:
                return self._cache[subshell_id].recv_socket

    def get_send_socket(self, subshell_id: str | None):
        if subshell_id is None:
            return self._parent_send_socket
        else:
            with self._lock:
                return self._cache[subshell_id].send_socket

    def list_subshell(self) -> list[str]:
        with self._lock:
            return list(self._cache)

    def subshell_id_from_thread_id(self, thread_id) -> str | None:
        """Return subshell_id of the specified thread_id.

        Raises RuntimeError if thread_id is not the main shell or a subshell.
        """
        with self._lock:
            if thread_id == main_thread().ident:
                return None
            for id, subshell in self._cache.items():
                if subshell.thread.ident == thread_id:
                    return id
            msg = f"Thread id '{thread_id} does not correspond to a subshell of this kernel"
            raise RuntimeError(msg)

    def _create_inproc_sockets(self, subshell_id: str | None):
        """Create a pair of inproc sockets to communicate with a subshell.
        """
        name = f"shell-{subshell_id}" if subshell_id else "shell"
        address = f"inproc://{name}"

        # Socket used in subshell thread to receive messages.
        recv_socket = self._context.socket(zmq.PAIR)
        recv_socket.bind(address)

        # Socket used in shell channel thread to send messages.
        send_socket = self._context.socket(zmq.PAIR)
        send_socket.connect(address)

        return send_socket, recv_socket

    def _stop_subshell(self, subshell: Subshell):
        thread = subshell.thread
        if thread and thread.is_alive():
            thread.stop()
            thread.join()

        for socket in (subshell.send_socket, subshell.recv_socket):
            if socket and not socket.closed:
                socket.close()
