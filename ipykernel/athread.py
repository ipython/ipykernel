import asyncio
import threading

import janus


class AThread(threading.Thread):
    """A thread that can run async tasks."""

    def __init__(self, name, awaitables=None):
        super().__init__(name=name, daemon=True)
        self._aws = list(awaitables) if awaitables is not None else []
        self._lock = threading.Lock()
        self.__initialized = False
        self._stopped = False

    def run(self):
        asyncio.run(self._main())

    async def _main(self):
        with self._lock:
            if self._stopped:
                return
            self._queue = janus.Queue()
            self.__initialized = True
        self._tasks = [asyncio.create_task(aw) for aw in self._aws]

        while True:
            try:
                aw = await self._queue.async_q.get()
            except BaseException:
                break
            if aw is None:
                break
            self._tasks.append(asyncio.create_task(aw))

        for task in self._tasks:
            task.cancel()

    def create_task(self, awaitable):
        """Create a task in the thread (thread-safe)."""
        with self._lock:
            if self.__initialized:
                self._queue.sync_q.put(awaitable)
            else:
                self._aws.append(awaitable)

    def stop(self):
        """Stop the thread (thread-safe)."""
        with self._lock:
            if self.__initialized:
                self._queue.sync_q.put(None)
            else:
                self._stopped = True
