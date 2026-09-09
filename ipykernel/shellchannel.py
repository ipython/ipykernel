"""A thread for a shell channel."""

from __future__ import annotations

import asyncio
from threading import current_thread
from typing import Any

import zmq
from zmq.eventloop.zmqstream import ZMQStream

from .subshell_manager import SubshellManager
from .thread import SHELL_CHANNEL_THREAD_NAME, BaseThread


class ShellChannelThread(BaseThread):
    """A thread for a shell channel.

    Communicates with shell/subshell threads via pairs of ZMQ inproc sockets.
    """

    def __init__(
        self,
        context: zmq.Context[Any],
        **kwargs,
    ):
        """Initialize the thread."""
        super().__init__(name=SHELL_CHANNEL_THREAD_NAME, **kwargs)
        self._manager: SubshellManager | None = None
        self._zmq_context = context  # Avoid use of self._context
        # Set by kernelapp.init_kernel after it builds the shell ZMQStream, since this
        # thread is created before the stream exists.
        self.shell_stream: ZMQStream | None = None
        # Record the parent thread - the thread that started the app (usually the main thread)
        self.parent_thread = current_thread()

        self.asyncio_lock = asyncio.Lock()

    @property
    def manager(self) -> SubshellManager:
        # Lazy initialisation.
        if self._manager is None:
            assert current_thread() == self.parent_thread
            # Also narrows the type for the manager, which takes a non-optional stream.
            assert self.shell_stream is not None
            self._manager = SubshellManager(
                self._zmq_context,
                self.io_loop,
                self.shell_stream,
            )
        return self._manager

    def run(self) -> None:
        """Run the thread."""
        try:
            super().run()
        finally:
            if self._manager:
                self._manager.close()
