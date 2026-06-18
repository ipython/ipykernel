"""Base class for threads."""

import asyncio
import sys
from threading import Thread

from tornado.ioloop import IOLoop

CONTROL_THREAD_NAME = "Control"
SHELL_CHANNEL_THREAD_NAME = "Shell channel"


def make_selector_io_loop() -> IOLoop:
    """Create a non-current tornado ``IOLoop`` for an ipykernel service thread.

    ipykernel runs its service channels -- control, IOPub, the shell channel and
    subshells -- on dedicated event loops in background threads. The process-wide
    asyncio loop on Windows is a ``ProactorEventLoop`` (so the main user-code loop
    can spawn asyncio subprocesses, see #1468/#1469), and Proactor has no native
    ``add_reader``. Tornado therefore drives a Proactor loop's zmq sockets through
    a helper "Tornado selector" thread. When a debugger suspends every thread at a
    breakpoint on Python >= 3.12 (``sys.monitoring``), that un-exempt helper thread
    freezes mid-wake and deadlocks the control/debug read path (#1469).

    These service loops never need Proactor's subprocess support, so we keep them
    on a ``SelectorEventLoop``: it implements ``add_reader`` natively and needs no
    helper thread. Only the main/user-code loop stays on Proactor. On non-Windows
    platforms the default loop is already selector-based, so this is a no-op there.
    """
    if sys.platform == "win32":
        return IOLoop(make_current=False, asyncio_loop=asyncio.SelectorEventLoop())
    return IOLoop(make_current=False)


class BaseThread(Thread):
    """Base class for threads."""

    def __init__(self, **kwargs):
        """Initialize the thread."""
        super().__init__(**kwargs)
        self.io_loop = make_selector_io_loop()
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True

    def run(self) -> None:
        """Run the thread."""
        try:
            self.io_loop.start()
        finally:
            self.io_loop.close()

    def stop(self) -> None:
        """Stop the thread.

        This method is threadsafe.
        """
        self.io_loop.add_callback(self.io_loop.stop)
