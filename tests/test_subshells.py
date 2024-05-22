"""Test kernel subshells."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from datetime import datetime, timedelta

from jupyter_client.blocking.client import BlockingKernelClient

from .utils import TIMEOUT, get_reply, get_replies, kernel


# Helpers

def create_subshell_helper(kc: BlockingKernelClient):
    msg = kc.session.msg("create_subshell_request")
    kc.control_channel.send(msg)
    msg_id = msg["header"]["msg_id"]
    reply = get_reply(kc, msg_id, TIMEOUT, channel="control")
    return reply["content"]


def delete_subshell_helper(kc: BlockingKernelClient, subshell_id: str):
    msg = kc.session.msg("delete_subshell_request", {"subshell_id": subshell_id})
    kc.control_channel.send(msg)
    msg_id = msg["header"]["msg_id"]
    reply = get_reply(kc, msg_id, TIMEOUT, channel="control")
    return reply["content"]


def list_subshell_helper(kc: BlockingKernelClient):
    msg = kc.session.msg("list_subshell_request")
    kc.control_channel.send(msg)
    msg_id = msg["header"]["msg_id"]
    reply = get_reply(kc, msg_id, TIMEOUT, channel="control")
    return reply["content"]


def execute_request_subshell_id(kc: BlockingKernelClient, code: str, subshell_id: str | None):
    msg = kc.session.msg("execute_request", {"code": code})
    msg["header"]["subshell_id"] = subshell_id
    msg_id = msg["msg_id"]
    kc.shell_channel.send(msg)
    while True:
        msg = kc.get_iopub_msg()
        # Get the stream message corresponding to msg_id
        if msg["msg_type"] == "stream" and msg["parent_header"]["msg_id"] == msg_id:
            content = msg["content"]
            #assert content["name"] == "stdout"
            break
    return content["text"].strip()


def execute_thread_count(kc: BlockingKernelClient) -> int:
    code = "import threading as t; print(t.active_count())"
    return int(execute_request_subshell_id(kc, code, None))


def execute_thread_ids(kc: BlockingKernelClient, subshell_id: str | None = None) -> tuple[str, str]:
    code = "import threading as t; print(t.get_ident(), t.main_thread().ident)"
    return execute_request_subshell_id(kc, code, subshell_id).split()


# Tests

def test_supported():
    with kernel() as kc:
        msg_id = kc.kernel_info()
        reply = get_reply(kc, msg_id, TIMEOUT)
        assert "supported_features" in reply["content"]
        assert "kernel subshells" in reply["content"]["supported_features"]


def test_subshell_id_lifetime():
    with kernel() as kc:
        assert list_subshell_helper(kc)["subshell_id"] == []
        subshell_id = create_subshell_helper(kc)["subshell_id"]
        assert list_subshell_helper(kc)["subshell_id"] == [subshell_id]
        delete_subshell_helper(kc, subshell_id)
        assert list_subshell_helper(kc)["subshell_id"] == []


def test_delete_non_existent():
    with kernel() as kc:
        reply = delete_subshell_helper(kc, "unknown_subshell_id")
        assert reply["status"] == "error"
        for key in ("ename", "evalue", "traceback"):
            assert key in reply


def test_thread_counts():
    with kernel() as kc:
        nthreads = execute_thread_count(kc)

        subshell_id = create_subshell_helper(kc)["subshell_id"]
        nthreads2 = execute_thread_count(kc)
        assert nthreads2 > nthreads

        delete_subshell_helper(kc, subshell_id)
        nthreads3 = execute_thread_count(kc)
        assert nthreads3 == nthreads


def test_thread_ids():
    with kernel() as kc:
        subshell_id = create_subshell_helper(kc)["subshell_id"]

        thread_id, main_thread_id = execute_thread_ids(kc)
        assert thread_id == main_thread_id

        thread_id, main_thread_id = execute_thread_ids(kc, subshell_id)
        assert thread_id != main_thread_id

        delete_subshell_helper(kc, subshell_id)


def test_run_concurrently():
    with kernel() as kc:
        subshell_id = create_subshell_helper(kc)["subshell_id"]

        # Prepare messages
        times = (0.05, 0.1)  # Sleep seconds. Test can fail with (0.05, 0.05)
        msgs = []
        for id, sleep in zip((None, subshell_id), times):
            code = f"import time; time.sleep({sleep})"
            msg = kc.session.msg("execute_request", {"code": code})
            msg["header"]["subshell_id"] = id
            msgs.append(msg)

        # Send messages
        start = datetime.now()
        for msg in msgs:
            kc.shell_channel.send(msg)

        _ = get_replies(kc, [msg["msg_id"] for msg in msgs])
        end = datetime.now()

        duration = end - start
        assert duration >= timedelta(seconds=max(times))
        assert duration < timedelta(seconds=sum(times))

        delete_subshell_helper(kc, subshell_id)


def test_execution_count():
    with kernel() as kc:
        subshell_id = create_subshell_helper(kc)["subshell_id"]

        # Prepare messages
        times = (0.1, 0.05, 0.2, 0.07)  # Sleep seconds
        msgs = []
        for id, sleep in zip((None, subshell_id, None, subshell_id), times):
            code = f"import time; time.sleep({sleep})"
            msg = kc.session.msg("execute_request", {"code": code})
            msg["header"]["subshell_id"] = id
            msgs.append(msg)

        for msg in msgs:
            kc.shell_channel.send(msg)

        # Wait for replies, may be in any order.
        replies = get_replies(kc, [msg["msg_id"] for msg in msgs])

        execution_counts = [r["content"]["execution_count"] for r in replies]
        ec = execution_counts[0]
        assert execution_counts == [ec, ec-1, ec+2, ec+1]

        delete_subshell_helper(kc, subshell_id)


def test_create_while_execute():
    with kernel() as kc:
        # Send request to execute code on main subshell.
        msg = kc.session.msg("execute_request", {"code": "import time; time.sleep(0.05)"})
        kc.shell_channel.send(msg)

        # Create subshell via control channel.
        control_msg = kc.session.msg("create_subshell_request")
        kc.control_channel.send(control_msg)
        control_reply = get_reply(kc, control_msg["header"]["msg_id"], TIMEOUT, channel="control")
        subshell_id = control_reply["content"]["subshell_id"]
        control_date = control_reply["header"]["date"]

        # Get result message from main subshell.
        shell_date = get_reply(kc, msg["msg_id"])["header"]["date"]

        delete_subshell_helper(kc, subshell_id)

        assert control_date < shell_date
