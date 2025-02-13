"""Base class for threads."""
from __future__ import annotations

from collections.abc import Awaitable
from queue import Queue
import typing as t
from threading import Event, Thread

from anyio import create_task_group, run, to_thread
from anyio.abc import TaskGroup

CONTROL_THREAD_NAME = "Control"
SHELL_CHANNEL_THREAD_NAME = "Shell channel"


class BaseThread(Thread):
    """Base class for threads."""

    def __init__(self, **kwargs):
        """Initialize the thread."""
        super().__init__(**kwargs)
        self.started = Event()
        self.stopped = Event()
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True
        self._tasks: Queue[tuple[str, t.Callable[[], Awaitable[t.Any]]] | None] = Queue()
        self._result: Queue[t.Any] = Queue()

    @property
    def task_group(self) -> TaskGroup:
        return self._task_group

    def start_soon(self, coro: t.Callable[[], Awaitable[t.Any]]) -> None:
        self._tasks.put(("start_soon", coro))

    def run_async(self, coro: t.Callable[[], Awaitable[t.Any]]) -> t.Any:
        self._tasks.put(("run_async", coro))
        return self._result.get()

    def run_sync(self, func: t.Callable[..., t.Any]) -> t.Any:
        self._tasks.put(("run_sync", func))
        return self._result.get()

    def run(self) -> None:
        """Run the thread."""
        try:
            run(self._main)
        except Exception:
            pass

    async def _main(self) -> None:
        async with create_task_group() as tg:
            self._task_group = tg
            self.started.set()
            while True:
                task = await to_thread.run_sync(self._tasks.get)
                if task is None:
                    break
                func, arg = task
                if func == "start_soon":
                    tg.start_soon(arg)
                elif func == "run_async":
                    res = await arg
                    self._result.put(res)
                else:  # func == "run_sync"
                    res = arg()
                    self._result.put(res)

            tg.cancel_scope.cancel()

    def stop(self) -> None:
        """Stop the thread.

        This method is threadsafe.
        """
        self._tasks.put(None)
        self.stopped.set()
