from threading import Thread

import zmq

if zmq.pyzmq_version_info() >= (17, 0):
    from tornado.ioloop import IOLoop
else:
    # deprecated since pyzmq 17
    from zmq.eventloop.ioloop import IOLoop


class ControlThread(Thread):
    def __init__(self, **kwargs):
        Thread.__init__(self, name="Control", **kwargs)
        self.io_loop = IOLoop(make_current=False)
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True

    def run(self):
        self.name = "Control"
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
