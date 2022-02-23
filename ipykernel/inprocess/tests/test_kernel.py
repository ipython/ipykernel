# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio
import sys
import unittest
from contextlib import contextmanager
from io import StringIO

import pytest
from IPython.utils.io import capture_output
from jupyter_client.session import Session

from ipykernel.inprocess.blocking import BlockingInProcessKernelClient
from ipykernel.inprocess.ipkernel import InProcessKernel
from ipykernel.inprocess.manager import InProcessKernelManager
from ipykernel.tests.utils import assemble_output

orig_msg = Session.msg


def _inject_cell_id(_self, *args, **kwargs):
    """
    This patch jupyter_client.session:Session.msg to add a cell_id to the return message metadata
    """
    assert isinstance(_self, Session)
    res = orig_msg(_self, *args, **kwargs)
    assert "cellId" not in res["metadata"]
    res["metadata"]["cellId"] = "test_cell_id"
    return res


@contextmanager
def patch_cell_id():
    try:
        Session.msg = _inject_cell_id
        yield
    finally:
        Session.msg = orig_msg


class InProcessKernelTestCase(unittest.TestCase):
    def setUp(self):
        self.km = InProcessKernelManager()
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready()

    def test_with_cell_id(self):

        with patch_cell_id():
            self.kc.execute("1+1")

    def test_pylab(self):
        """Does %pylab work in the in-process kernel?"""
        _ = pytest.importorskip("matplotlib", reason="This test requires matplotlib")
        kc = self.kc
        kc.execute("%pylab")
        out, err = assemble_output(kc.get_iopub_msg)
        self.assertIn("matplotlib", out)

    def test_raw_input(self):
        """Does the in-process kernel handle raw_input correctly?"""
        io = StringIO("foobar\n")
        sys_stdin = sys.stdin
        sys.stdin = io
        try:
            self.kc.execute("x = input()")
        finally:
            sys.stdin = sys_stdin
        assert self.km.kernel.shell.user_ns.get("x") == "foobar"

    @pytest.mark.skipif("__pypy__" in sys.builtin_module_names, reason="fails on pypy")
    def test_stdout(self):
        """Does the in-process kernel correctly capture IO?"""
        kernel = InProcessKernel()

        with capture_output() as io:
            kernel.shell.run_cell('print("foo")')
        assert io.stdout == "foo\n"

        kc = BlockingInProcessKernelClient(kernel=kernel, session=kernel.session)
        kernel.frontends.append(kc)
        kc.execute('print("bar")')
        out, err = assemble_output(kc.get_iopub_msg)
        assert out == "bar\n"

    @pytest.mark.skip(reason="Currently don't capture during test as pytest does its own capturing")
    def test_capfd(self):
        """Does correctly capture fd"""
        kernel = InProcessKernel()

        with capture_output() as io:
            kernel.shell.run_cell('print("foo")')
        assert io.stdout == "foo\n"

        kc = BlockingInProcessKernelClient(kernel=kernel, session=kernel.session)
        kernel.frontends.append(kc)
        kc.execute("import os")
        kc.execute('os.system("echo capfd")')
        out, err = assemble_output(kc.iopub_channel)
        assert out == "capfd\n"

    def test_getpass_stream(self):
        "Tests that kernel getpass accept the stream parameter"
        kernel = InProcessKernel()
        kernel._allow_stdin = True
        kernel._input_request = lambda *args, **kwargs: None

        kernel.getpass(stream="non empty")

    def test_do_execute(self):
        kernel = InProcessKernel()
        asyncio.run(kernel.do_execute("a=1", True))
        assert kernel.shell.user_ns["a"] == 1
