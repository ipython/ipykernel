import asyncio
from threading import Thread


class ControlThread(Thread):
    def __init__(self, **kwargs):
        Thread.__init__(self, name="Control", **kwargs)
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True
        self.io_loop = asyncio.new_event_loop()

    def run(self):
        self.name = "Control"
        asyncio.set_event_loop(self.io_loop)
        try:
            self.io_loop.run_forever()
        finally:
            self.io_loop.close()

    def stop(self):
        """Stop the thread.

        This method is threadsafe.
        """
        self.io_loop.call_soon_threadsafe(self.io_loop.stop)
