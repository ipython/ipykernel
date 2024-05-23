"""A cache for subshell information."""
# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from dataclasses import dataclass
from threading import Lock, main_thread
import zmq

from .subshell import SubshellThread


@dataclass
class Subshell:
    thread: SubshellThread
    send_socket: zmq.Socket
    recv_socket: zmq.Socket


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
    def __init__(self, context: zmq.Context):
        self._context: zmq.Context = context
        self._cache: dict[str, Subshell] = {}
        self._lock: Lock = Lock()

        # Parent subshell sockets.
        self._parent_send_socket, self._parent_recv_socket = \
            self._create_inproc_sockets(None)

    def close(self):
        for socket in (self._parent_send_socket, self._parent_recv_socket):
            if socket and not socket.closed:
                socket.close()

        self._parent_recv_socket = None
        self._parent_send_socket = None

        with self._lock:
            while True:
                try:
                    _, subshell = self._cache.popitem()
                except KeyError:
                    break
                self._stop_subshell(subshell)

    def create(self, subshell_id: str, thread: SubshellThread) -> None:
        # check if subshell_id already exists...
        # assume it doesn't

        with self._lock:
            assert subshell_id not in self._cache
            send_socket, recv_socket = self._create_inproc_sockets(subshell_id)
            self._cache[subshell_id] = Subshell(thread, send_socket, recv_socket)

    def delete(self, subshell_id: str) -> None:
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

    def list(self) -> list[str]:
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
