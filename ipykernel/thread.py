"""Base class for threads."""
import typing as t
from threading import Event, Thread

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
        self.__stop = Event()
        self._tasks_and_args: t.List[t.Tuple[t.Callable, t.Tuple]] = []

    def add_task(self, task: t.Callable, *args: t.Tuple):
        # May only add tasks before the thread is started.
        self._tasks_and_args.append((task, args))

    def run(self) -> t.Any:
        """Run the thread."""
        return run(self._main)

    async def _main(self) -> None:
        async with create_task_group() as tg:
            for task, args in self._tasks_and_args:
                tg.start_soon(task, *args)
            await to_thread.run_sync(self.__stop.wait)
            tg.cancel_scope.cancel()

    def stop(self):
        """Stop the thread.

        This method is threadsafe.
        """
        self.__stop.set()
