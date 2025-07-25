"""Pair of ZMQ inproc sockets used for communication between threads."""

from __future__ import annotations

from typing import Any

import zmq
from tornado.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream


class SocketPair:
    """Pair of ZMQ inproc sockets for one-direction communication between 2 threads.

    One of the threads is always the shell_channel_thread, the other may be the control
    thread, main thread or a subshell thread.

    .. versionadded:: 7
    """

    from_socket: zmq.Socket[Any]
    to_socket: zmq.Socket[Any]
    to_stream: ZMQStream | None = None
    on_recv_callback: Any
    on_recv_copy: bool

    def __init__(self, context: zmq.Context[Any], name: str):
        """Initialize the inproc socker pair."""
        self.from_socket = context.socket(zmq.PAIR)
        self.to_socket = context.socket(zmq.PAIR)
        address = self._address(name)
        self.from_socket.bind(address)
        self.to_socket.connect(address)  # Or do I need to do this in another thread?

    def close(self):
        """Close the inproc socker pair."""
        self.from_socket.close()

        if self.to_stream is not None:
            self.to_stream.close()
        self.to_socket.close()

    def on_recv(self, io_loop: IOLoop, on_recv_callback, copy: bool = False):
        """Set the callback used when a message is received on the to stream."""
        # io_loop is that of the 'to' thread.
        self.on_recv_callback = on_recv_callback
        self.on_recv_copy = copy
        if self.to_stream is None:
            self.to_stream = ZMQStream(self.to_socket, io_loop)
        self.resume_on_recv()

    def pause_on_recv(self):
        """Pause receiving on the to stream."""
        if self.to_stream is not None:
            self.to_stream.stop_on_recv()

    def resume_on_recv(self):
        """Resume receiving on the to stream."""
        if self.to_stream is not None and not self.to_stream.closed():
            self.to_stream.on_recv(self.on_recv_callback, copy=self.on_recv_copy)

    def _address(self, name) -> str:
        """Return the address used for this inproc socket pair."""
        return f"inproc://subshell{name}"
