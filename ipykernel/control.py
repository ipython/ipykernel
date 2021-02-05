
from threading import Thread
import zmq
if zmq.pyzmq_version_info() >= (17, 0):
    from tornado.ioloop import IOLoop
else:
    # deprecated since pyzmq 17
    from zmq.eventloop.ioloop import IOLoop


class ControlThread(Thread):

    def __init__(self, **kwargs):
        Thread.__init__(self, **kwargs)
        self.io_loop = IOLoop(make_current=False)

    def run(self): 
        self.io_loop.make_current()
        self.io_loop.start()
        self.io_loop.close(all_fds=True)
