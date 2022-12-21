from .athread import AThread


class ControlThread(AThread):
    """A thread for a control channel."""

    def __init__(self):
        """Initialize the thread."""
        super().__init__(name="Control")
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True
