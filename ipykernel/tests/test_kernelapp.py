import os
import signal
import sys
import threading
import time
from unittest.mock import MagicMock

import pytest

from ipykernel.kernelapp import IPKernelApp, main

from .conftest import MockKernel

try:
    import trio
except ImportError:
    trio = None


@pytest.mark.skipif(os.name == "nt", reason="requires ipc")
def test_init_ipc_socket():
    app = IPKernelApp(transport="ipc")
    app.init_sockets()
    app.cleanup_connection_file()
    app.close()


def test_blackhole():
    app = IPKernelApp()
    app.no_stderr = True
    app.no_stdout = True
    app.init_blackhole()


@pytest.mark.skipif(trio is None, reason="requires trio")
def test_trio_loop():
    app = IPKernelApp(trio_loop=True)
    app.kernel = MockKernel()
    app.kernel.shell = MagicMock()

    def trigger_kb_interrupt():
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGINT)

    thread = threading.Thread(target=trigger_kb_interrupt)
    thread.start()
    app.init_sockets()
    with pytest.raises(Exception) as e:
        app.start()
    assert str(e.value) == "Kernel interrupted but no cell is running"
    app.cleanup_connection_file()
    app.kernel.destroy()
    app.close()


def test_main():
    def trigger_kb_interrupt():
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGQUIT)

    def process_quit(*args, **kwargs):
        sys.exit(0)

    thread = threading.Thread(target=trigger_kb_interrupt)
    signal.signal(signal.SIGQUIT, process_quit)
    thread.start()

    with pytest.raises(SystemExit):
        sys.argv = sys.argv[:1]
        main()
    IPKernelApp.clear_instance()
