"""A thread for a control channel."""

from .thread import BaseThread

CONTROL_THREAD_NAME = "Control"


class ControlThread(BaseThread):
    """A thread for a control channel."""

    def __init__(self, **kwargs):
        """Initialize the thread."""
        super().__init__(name=CONTROL_THREAD_NAME, **kwargs)

    def run(self):
        """Run the thread."""
        self.name = CONTROL_THREAD_NAME
        super().run()
