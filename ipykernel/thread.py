"""Base class for threads."""
from __future__ import annotations

from collections.abc import Awaitable
from queue import Queue
from threading import Thread
from typing import Callable

from anyio import create_task_group, run, to_thread

CONTROL_THREAD_NAME = "Control"
SHELL_CHANNEL_THREAD_NAME = "Shell channel"


class BaseThread(Thread):
    """Base class for threads."""

    def __init__(self, **kwargs):
        """Initialize the thread."""
        super().__init__(**kwargs)
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True
        self._tasks: Queue[Callable[[], Awaitable[None]] | None] = Queue()

    def start_soon(self, task: Callable[[], Awaitable[None]] | None) -> None:
        self._tasks.put(task)

    def run(self) -> None:
        """Run the thread."""
        run(self._main)

    async def _main(self) -> None:
        async with create_task_group() as tg:
            while True:
                task = await to_thread.run_sync(self._tasks.get)
                if task is None:
                    break
                tg.start_soon(task)
            tg.cancel_scope.cancel()

    def stop(self) -> None:
        """Stop the thread.

        This method is threadsafe.
        """
        self._tasks.put(None)
