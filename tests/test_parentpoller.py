import os
import sys
import warnings
from unittest import mock

import pytest

from ipykernel.parentpoller import ParentPollerUnix, ParentPollerWindows


@pytest.mark.skipif(os.name == "nt", reason="only works on posix")
def test_parent_poller_unix_to_pid1():
    poller = ParentPollerUnix()
    with mock.patch("os.getppid", lambda: 1):  # noqa: PT008

        def exit_mock(*args):
            sys.exit(1)

        with mock.patch("os._exit", exit_mock), pytest.raises(SystemExit):
            poller.run()

    def mock_getppid():
        msg = "hi"
        raise ValueError(msg)

    with mock.patch("os.getppid", mock_getppid), pytest.raises(ValueError):  # noqa: PT011
        poller.run()


@pytest.mark.skipif(os.name == "nt", reason="only works on posix")
def test_parent_poller_unix_reparent_not_pid1():
    parent_pid = 221
    parent_pids = iter([parent_pid, parent_pid - 1])

    poller = ParentPollerUnix(parent_pid=parent_pid)

    with mock.patch("os.getppid", lambda: next(parent_pids)):  # noqa: PT008

        def exit_mock(*args):
            sys.exit(1)

        with mock.patch("os._exit", exit_mock), pytest.raises(SystemExit):
            poller.run()


@pytest.mark.skipif(os.name != "nt", reason="only works on windows")
def test_parent_poller_windows():
    poller = ParentPollerWindows(interrupt_handle=1)

    def mock_wait(*args, **kwargs):
        return -1

    with mock.patch("ctypes.windll.kernel32.WaitForMultipleObjects", mock_wait):  # noqa
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            poller.run()
