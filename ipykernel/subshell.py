"""A thread for a subshell."""

from typing import Any

import zmq
from zmq.eventloop.zmqstream import ZMQStream

from .thread import BaseThread
from .utils import create_inproc_pair_socket


class SubshellThread(BaseThread):
    """A thread for a subshell."""

    def __init__(
        self,
        subshell_id: str,
        context: zmq.Context[Any],
        **kwargs,
    ):
        """Initialize the thread."""
        super().__init__(name=f"subshell-{subshell_id}", **kwargs)

        shell_channel_socket = create_inproc_pair_socket(context, subshell_id, True)
        # io_loop will be current io_loop which is of ShellChannelThread
        self.shell_channel_stream = ZMQStream(shell_channel_socket)

        subshell_socket = create_inproc_pair_socket(context, subshell_id, False)
        self.subshell_stream = ZMQStream(subshell_socket, self.io_loop)

        # When aborting flag is set, execute_request messages to this subshell will be aborted.
        self.aborting = False

    def run(self) -> None:
        try:
            super().run()
        finally:
            self.subshell_stream.close()
            self.shell_channel_stream.close()
