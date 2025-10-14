"""A thread for a shell channel."""

from __future__ import annotations

import asyncio
from typing import Any

import zmq

from .subshell_manager import SubshellManager
from .thread import SHELL_CHANNEL_THREAD_NAME, BaseThread


class ShellChannelThread(BaseThread):
    """A thread for a shell channel.

    Communicates with shell/subshell threads via pairs of ZMQ inproc sockets.
    """

    def __init__(
        self,
        context: zmq.Context[Any],
        shell_socket: zmq.Socket[Any],
        **kwargs,
    ):
        """Initialize the thread."""
        super().__init__(name=SHELL_CHANNEL_THREAD_NAME, **kwargs)
        self._manager: SubshellManager | None = None
        self._zmq_context = context  # Avoid use of self._context
        self._shell_socket = shell_socket

        self.asyncio_lock = asyncio.Lock()

    @property
    def manager(self) -> SubshellManager:
        # Lazy initialisation.
        if self._manager is None:
            self._manager = SubshellManager(
                self._zmq_context,
                self.io_loop,
                self._shell_socket,
            )
        return self._manager

    def run(self) -> None:
        """Run the thread."""
        try:
            super().run()
        finally:
            if self._manager:
                self._manager.close()
