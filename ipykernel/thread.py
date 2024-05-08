"""Base class for threads."""
from threading import Event, Thread

from anyio import create_task_group, run, to_thread


class BaseThread(Thread):
    """Base class for threads."""

    def __init__(self, name, **kwargs):
        """Initialize the thread."""
        Thread.__init__(self, name=name, **kwargs)
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True
        self.__stop = Event()
        self._task = None

    def set_task(self, task):
        self._task = task

    def run(self):
        """Run the thread."""
        run(self._main)

    async def _main(self):
        async with create_task_group() as tg:
            if self._task is not None:
                tg.start_soon(self._task)
            await to_thread.run_sync(self.__stop.wait)
            tg.cancel_scope.cancel()

    def stop(self):
        """Stop the thread.

        This method is threadsafe.
        """
        self.__stop.set()
