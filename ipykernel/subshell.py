"""A thread for a subshell."""

from .thread import BaseThread


class SubshellThread(BaseThread):
    """A thread for a subshell.
    """

    def __init__(self, subshell_id: str, **kwargs):
        """Initialize the thread."""
        super().__init__(name=f"subshell-{subshell_id}", **kwargs)
