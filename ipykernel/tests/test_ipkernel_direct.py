"""Test IPythonKernel directly"""

import asyncio
import os

import pytest
import zmq
from IPython.core.history import DummyDB

from ipykernel.ipkernel import BaseComm, IPythonKernel, create_comm

from .conftest import MockIPyKernel

if os.name == "nt":
    pytest.skip("skipping tests on windows", allow_module_level=True)


class user_mod:
    __dict__ = {}


async def test_properities(ipkernel: IPythonKernel):
    ipkernel.user_module = user_mod()
    ipkernel.user_ns = {}


async def test_direct_kernel_info_request(ipkernel):
    reply = await ipkernel.test_shell_message("kernel_info_request", {})
    assert reply["header"]["msg_type"] == "kernel_info_reply"


async def test_direct_execute_request(ipkernel: MockIPyKernel):
    reply = await ipkernel.test_shell_message("execute_request", dict(code="hello", silent=False))
    assert reply["header"]["msg_type"] == "execute_reply"
    reply = await ipkernel.test_shell_message(
        "execute_request", dict(code="trigger_error", silent=False)
    )
    assert reply["content"]["status"] == "aborted"

    ipkernel.shell.should_run_async = False
    reply = await ipkernel.test_shell_message("execute_request", dict(code="hello", silent=False))
    assert reply["header"]["msg_type"] == "execute_reply"


async def test_direct_execute_request_aborting(ipkernel):
    ipkernel._aborting = True
    reply = await ipkernel.test_shell_message("execute_request", dict(code="hello", silent=False))
    assert reply["header"]["msg_type"] == "execute_reply"
    assert reply["content"]["status"] == "aborted"


async def test_complete_request(ipkernel):
    reply = await ipkernel.test_shell_message("complete_request", dict(code="hello", cursor_pos=0))
    assert reply["header"]["msg_type"] == "complete_reply"
    ipkernel.use_experimental_completions = False
    reply = await ipkernel.test_shell_message("complete_request", dict(code="hello", cursor_pos=4))
    assert reply["header"]["msg_type"] == "complete_reply"


async def test_inspect_request(ipkernel):
    reply = await ipkernel.test_shell_message("inspect_request", dict(code="hello", cursor_pos=0))
    assert reply["header"]["msg_type"] == "inspect_reply"


async def test_history_request(ipkernel):
    ipkernel.shell.history_manager.db = DummyDB()
    reply = await ipkernel.test_shell_message(
        "history_request", dict(hist_access_type="", output="", raw="")
    )
    assert reply["header"]["msg_type"] == "history_reply"
    reply = await ipkernel.test_shell_message(
        "history_request", dict(hist_access_type="tail", output="", raw="")
    )
    assert reply["header"]["msg_type"] == "history_reply"
    reply = await ipkernel.test_shell_message(
        "history_request", dict(hist_access_type="range", output="", raw="")
    )
    assert reply["header"]["msg_type"] == "history_reply"
    reply = await ipkernel.test_shell_message(
        "history_request", dict(hist_access_type="search", output="", raw="")
    )
    assert reply["header"]["msg_type"] == "history_reply"


async def test_comm_info_request(ipkernel):
    reply = await ipkernel.test_shell_message("comm_info_request")
    assert reply["header"]["msg_type"] == "comm_info_reply"


async def test_direct_interrupt_request(ipkernel):
    reply = await ipkernel.test_shell_message("interrupt_request", {})
    assert reply["header"]["msg_type"] == "interrupt_reply"


# TODO: this causes deadlock
# async def test_direct_shutdown_request(ipkernel):
#     reply = await ipkernel.test_shell_message("shutdown_request", dict(restart=False))
#     assert reply["header"]["msg_type"] == "shutdown_reply"
#     reply = await ipkernel.test_shell_message("shutdown_request", dict(restart=True))
#     assert reply["header"]["msg_type"] == "shutdown_reply"

# TODO: this causes deadlock
# async def test_direct_usage_request(kernel):
#     reply = await kernel.test_control_message("usage_request", {})
#     assert reply['header']['msg_type'] == 'usage_reply'


async def test_is_complete_request(ipkernel: MockIPyKernel):
    reply = await ipkernel.test_shell_message("is_complete_request", dict(code="hello"))
    assert reply["header"]["msg_type"] == "is_complete_reply"
    setattr(ipkernel, "shell.input_transformer_manager", None)
    reply = await ipkernel.test_shell_message("is_complete_request", dict(code="hello"))
    assert reply["header"]["msg_type"] == "is_complete_reply"


def test_do_apply(ipkernel: MockIPyKernel):
    ipkernel.do_apply({}, [], "abc", {})


async def test_direct_debug_request(ipkernel):
    reply = await ipkernel.test_control_message("debug_request", {})
    assert reply["header"]["msg_type"] == "debug_reply"


async def test_direct_clear(ipkernel):
    ipkernel.do_clear()


async def test_cancel_on_sigint(ipkernel: IPythonKernel):
    future = asyncio.Future()
    with ipkernel._cancel_on_sigint(future):
        pass
    future.set_result(None)


def test_dispatch_debugpy(ipkernel: IPythonKernel):
    msg = ipkernel.session.msg("debug_request", {})
    msg_list = ipkernel.session.serialize(msg)
    ipkernel.dispatch_debugpy([zmq.Message(m) for m in msg_list])


async def test_start(ipkernel: IPythonKernel):
    ipkernel.start()
    ipkernel.debugpy_stream = None
    ipkernel.start()


def test_create_comm():
    assert isinstance(create_comm(), BaseComm)


def test_finish_metadata(ipkernel: IPythonKernel):
    reply_content = dict(status="error", ename="UnmetDependency")
    metadata = ipkernel.finish_metadata({}, {}, reply_content)
    assert metadata["dependencies_met"] is False


async def test_do_debug_request(ipkernel: IPythonKernel):
    msg = ipkernel.session.msg("debug_request", {})
    msg_list = ipkernel.session.serialize(msg)
    await ipkernel.do_debug_request(msg)
