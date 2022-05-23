from threading import Thread

import zmq
import psutil

if zmq.pyzmq_version_info() >= (17, 0):
    from tornado.ioloop import IOLoop
else:
    # deprecated since pyzmq 17
    from zmq.eventloop.ioloop import IOLoop

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ControlThread(Thread):
    processes = {}

    def __init__(self, **kwargs):
        Thread.__init__(self, name="Control", **kwargs)
        self.io_loop = IOLoop(make_current=False)
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True
        self.cpu_percent = psutil.cpu_percent()

    def run(self):
        self.name = "Control"
        self.io_loop.make_current()
        try:
            self.io_loop.start()
        finally:
            self.io_loop.close()

    def get_process_metric_value(self, process, name, attribute=None):
        try:
            # psutil.Process methods will either return...
            pid = process.pid
            p = self.processes.get(pid, None)
            if not p:
                self.processes[process.pid] = process
            p = self.processes.get(pid)
            metric_value = getattr(p, name)()
            if attribute is not None:  # ... a named tuple
                return getattr(metric_value, attribute)
            else:  # ... or a number
                return metric_value
        # Avoid littering logs with stack traces
        # complaining about dead processes
        except BaseException:
            return None

    def stop(self):
        """Stop the thread.

        This method is threadsafe.
        """
        self.io_loop.add_callback(self.io_loop.stop)
