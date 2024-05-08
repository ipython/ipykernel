"""A thread for a shell channel."""

import zmq

from .thread import BaseThread

SHELL_CHANNEL_THREAD_NAME = "Shell channel"


class ShellChannelThread(BaseThread):
    """A thread for a shell channel.

    Communicates with shell execute threads via pairs of ZMQ inproc sockets.
    """

    def __init__(self, context, **kwargs):
        """Initialize the thread."""
        super().__init__(name=SHELL_CHANNEL_THREAD_NAME, **kwargs)
        self._context = context

    def create_inproc_sockets(self):
        # Socket used in another thread to receive messages from this thread.
        self._recv_socket = self._context.socket(zmq.PAIR)
        self._recv_socket.bind(f"inproc://shell")

        # Socket used in this thread to send messages.
        self._send_socket = self._context.socket(zmq.PAIR)
        self._send_socket.connect(f"inproc://shell")

        return self._recv_socket

    def get_send_inproc_socket(self):
        return self._send_socket

    def run(self):
        """Run the thread."""
        self.name = SHELL_CHANNEL_THREAD_NAME
        super().run()

        for socket in (self._send_socket, self._recv_socket):
            if socket and not socket.closed:
                socket.close()
