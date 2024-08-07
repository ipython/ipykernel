"""A thread for a subshell."""

from threading import current_thread

import zmq.asyncio

from .thread import BaseThread


class SubshellThread(BaseThread):
    """A thread for a subshell."""

    def __init__(self, subshell_id: str, **kwargs):
        """Initialize the thread."""
        super().__init__(name=f"subshell-{subshell_id}", **kwargs)

        # Inproc PAIR socket, for communication with shell channel thread.
        self._pair_socket: zmq.asyncio.Socket | None = None

    async def create_pair_socket(self, context: zmq.asyncio.Context, address: str):
        """Create inproc PAIR socket, for communication with shell channel thread.

        Should be called from this thread, so usually via add_task before the
        thread is started.
        """
        assert current_thread() == self
        self._pair_socket = context.socket(zmq.PAIR)
        self._pair_socket.connect(address)

    def run(self):
        super().run()

        if self._pair_socket is not None:
            self._pair_socket.close()
            self._pair_socket = None
