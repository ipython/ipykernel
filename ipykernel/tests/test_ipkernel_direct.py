"""Test IPythonKernel directly"""

import asyncio
import os

import pytest

from ipykernel.ipkernel import IPythonKernel

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


async def test_direct_execute_request(ipkernel):
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


async def test_inspect_request(ipkernel):
    reply = await ipkernel.test_shell_message("inspect_request", dict(code="hello", cursor_pos=0))
    assert reply["header"]["msg_type"] == "inspect_reply"


async def test_history_request(ipkernel):
    reply = await ipkernel.test_shell_message(
        "history_request", dict(hist_access_type="", output="", raw="")
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


async def test_is_complete_request(ipkernel):
    reply = await ipkernel.test_shell_message("is_complete_request", dict(code="hello"))
    assert reply["header"]["msg_type"] == "is_complete_reply"


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
