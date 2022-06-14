from threading import Thread

import zmq

if zmq.pyzmq_version_info() >= (17, 0):
    from tornado.ioloop import IOLoop
else:
    # deprecated since pyzmq 17
    from zmq.eventloop.ioloop import IOLoop


class ShellThread(Thread):
    def __init__(self, **kwargs):
        self._shell_id = kwargs.pop("shell_id")
        Thread.__init__(self, name=f"Shell_{self._shell_id}", **kwargs)
        self.io_loop = IOLoop(make_current=False)

    def run(self):
        self.name = f"Shell_{self._shell_id}"
        self.io_loop.make_current()
        try:
            self.io_loop.start()
        finally:
            self.io_loop.close()

    def stop(self):
        """Stop the thread.

        This method is threadsafe.
        """
        self.io_loop.add_callback(self.io_loop.stop)
