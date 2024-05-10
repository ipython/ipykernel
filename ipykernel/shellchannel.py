"""A thread for a shell channel."""

from .subshell_cache import SubshellCache
from .thread import BaseThread

SHELL_CHANNEL_THREAD_NAME = "Shell channel"


class ShellChannelThread(BaseThread):
    """A thread for a shell channel.

    Communicates with shell execute threads via pairs of ZMQ inproc sockets.
    """

    def __init__(self, context, **kwargs):
        """Initialize the thread."""
        super().__init__(name=SHELL_CHANNEL_THREAD_NAME, **kwargs)
        self._cache: SubshellCache | None = None
        self._context = context

    @property
    def cache(self):
        if self._cache is None:
            self._cache = SubshellCache(self._context)
        return self._cache

    def run(self):
        """Run the thread."""
        self.name = SHELL_CHANNEL_THREAD_NAME
        super().run()

        if self._cache:
            self._cache.close()
