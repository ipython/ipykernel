"""Test kernel subshells."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import platform
import time
from collections import Counter
from queue import Empty

import pytest
from jupyter_client.blocking.client import BlockingKernelClient

from .utils import (
    TIMEOUT,
    assemble_output,
    flush_channels,
    get_replies,
    get_reply,
    new_kernel,
    wait_for_idle,
)

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


def execute_request(
    kc: BlockingKernelClient, code: str, subshell_id: str | None, silent: bool = False
):
    msg = kc.session.msg("execute_request", {"code": code, "silent": silent})
    msg["header"]["subshell_id"] = subshell_id
    kc.shell_channel.send(msg)
    return msg


def execute_request_subshell_id(
    kc: BlockingKernelClient, code: str, subshell_id: str | None, terminator: str = "\n"
):
    msg = execute_request(kc, code, subshell_id)
    msg_id = msg["header"]["msg_id"]
    stdout, _ = assemble_output(kc.get_iopub_msg, None, msg_id)
    return stdout.strip()


def execute_thread_count(kc: BlockingKernelClient) -> int:
    code = "print(threading.active_count())"
    return int(execute_request_subshell_id(kc, code, None))


def execute_thread_ids(kc: BlockingKernelClient, subshell_id: str | None = None) -> tuple[str, str]:
    code = "print(threading.get_ident(), threading.main_thread().ident)"
    return execute_request_subshell_id(kc, code, subshell_id).split()


# Tests


def test_no_subshells():
    with new_kernel() as kc:
        # Test operation of separate channel thread without using any subshells.
        execute_request_subshell_id(kc, "a = 2*3", None)
        res = execute_request_subshell_id(kc, "print(a)", None)
        assert res == "6"


def test_supported():
    with new_kernel() as kc:
        msg_id = kc.kernel_info()
        reply = get_reply(kc, msg_id, TIMEOUT)
        assert "supported_features" in reply["content"]
        assert "kernel subshells" in reply["content"]["supported_features"]


def test_subshell_id_lifetime():
    with new_kernel() as kc:
        assert list_subshell_helper(kc)["subshell_id"] == []
        subshell_id = create_subshell_helper(kc)["subshell_id"]
        assert list_subshell_helper(kc)["subshell_id"] == [subshell_id]
        delete_subshell_helper(kc, subshell_id)
        assert list_subshell_helper(kc)["subshell_id"] == []


def test_thread_counts():
    with new_kernel() as kc:
        execute_request_subshell_id(kc, "import threading", None)
        nthreads = execute_thread_count(kc)

        subshell_id = create_subshell_helper(kc)["subshell_id"]
        nthreads2 = execute_thread_count(kc)
        assert nthreads2 > nthreads

        delete_subshell_helper(kc, subshell_id)
        nthreads3 = execute_thread_count(kc)
        assert nthreads3 == nthreads


def test_thread_ids():
    with new_kernel() as kc:
        execute_request_subshell_id(kc, "import threading", None)
        subshell_id = create_subshell_helper(kc)["subshell_id"]

        thread_id, main_thread_id = execute_thread_ids(kc)
        assert thread_id == main_thread_id

        thread_id, main_thread_id = execute_thread_ids(kc, subshell_id)  # This is the problem
        assert thread_id != main_thread_id

        delete_subshell_helper(kc, subshell_id)


@pytest.mark.parametrize("are_subshells", [(False, True), (True, False), (True, True)])
@pytest.mark.parametrize("overlap", [True, False])
def test_run_concurrently_sequence(are_subshells, overlap, request):
    if request.config.getvalue("--cov"):
        pytest.skip("Skip time-sensitive subshell tests if measuring coverage")

    with new_kernel() as kc:
        subshell_ids = [
            create_subshell_helper(kc)["subshell_id"] if is_subshell else None
            for is_subshell in are_subshells
        ]

        # Import time module before running time-sensitive subshell code
        # and use threading.Barrier to synchronise start of subshell code.
        execute_request_subshell_id(
            kc, "import threading as t, time; b=t.Barrier(2); print('ok')", None
        )

        sleep = 0.5
        if overlap:
            codes = [
                f"b.wait(); start0=True; end0=False; time.sleep({sleep}); end0=True",
                f"b.wait(); time.sleep({sleep / 2}); assert start0; assert not end0; time.sleep({sleep}); assert end0",
            ]
        else:
            codes = [
                f"b.wait(); start0=True; end0=False; time.sleep({sleep}); assert end1",
                f"b.wait(); time.sleep({sleep / 2}); assert start0; assert not end0; end1=True",
            ]

        msgs = []
        for subshell_id, code in zip(subshell_ids, codes, strict=False):
            msg = kc.session.msg("execute_request", {"code": code})
            msg["header"]["subshell_id"] = subshell_id
            kc.shell_channel.send(msg)
            msgs.append(msg)

        replies = get_replies(kc, [msg["msg_id"] for msg in msgs], timeout=None)

        for subshell_id in subshell_ids:
            if subshell_id:
                delete_subshell_helper(kc, subshell_id)

        for reply in replies:
            assert reply["content"]["status"] == "ok", reply


def test_create_while_execute():
    with new_kernel() as kc:
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


@pytest.mark.skipif(
    platform.python_implementation() == "PyPy",
    reason="does not work on PyPy",
)
def test_shutdown_with_subshell():
    # Based on test_kernel.py::test_shutdown
    with new_kernel() as kc:
        km = kc.parent
        subshell_id = create_subshell_helper(kc)["subshell_id"]
        assert list_subshell_helper(kc)["subshell_id"] == [subshell_id]
        kc.shutdown()
        for _ in range(100):  # 10 s timeout
            if km.is_alive():
                time.sleep(0.1)
            else:
                break
        assert not km.is_alive()


@pytest.mark.parametrize("are_subshells", [(False, True), (True, False), (True, True)])
def test_execute_stop_on_error(are_subshells):
    # Based on test_message_spec.py::test_execute_stop_on_error, testing that exception
    # in one subshell aborts execution queue in that subshell but not others.
    with new_kernel() as kc:
        subshell_ids = [
            create_subshell_helper(kc)["subshell_id"] if is_subshell else None
            for is_subshell in are_subshells
        ]

        msg_ids = []

        msg = execute_request(
            kc, "import asyncio; await asyncio.sleep(1); raise ValueError()", subshell_ids[0]
        )
        msg_ids.append(msg["header"]["msg_id"])
        msg = execute_request(kc, "print('hello')", subshell_ids[0])
        msg_ids.append(msg["header"]["msg_id"])
        msg = execute_request(kc, "print('goodbye')", subshell_ids[0])
        msg_ids.append(msg["header"]["msg_id"])

        msg = execute_request(kc, "import time; time.sleep(1.5)", subshell_ids[1])
        msg_ids.append(msg["header"]["msg_id"])
        msg = execute_request(kc, "print('other')", subshell_ids[1])
        msg_ids.append(msg["header"]["msg_id"])

        replies = get_replies(kc, msg_ids)

        assert replies[0]["parent_header"]["subshell_id"] == subshell_ids[0]
        assert replies[1]["parent_header"]["subshell_id"] == subshell_ids[0]
        assert replies[2]["parent_header"]["subshell_id"] == subshell_ids[0]
        assert replies[3]["parent_header"]["subshell_id"] == subshell_ids[1]
        assert replies[4]["parent_header"]["subshell_id"] == subshell_ids[1]

        assert replies[0]["content"]["status"] == "error"
        assert replies[1]["content"]["status"] == "aborted"
        assert replies[2]["content"]["status"] == "aborted"
        assert replies[3]["content"]["status"] == "ok"
        assert replies[4]["content"]["status"] == "ok"

        # Check abort is cleared.
        msg = execute_request(kc, "print('check')", subshell_ids[0])
        reply = get_reply(kc, msg["msg_id"])
        assert reply["parent_header"]["subshell_id"] == subshell_ids[0]
        assert reply["content"]["status"] == "ok"

        # Cleanup
        for subshell_id in subshell_ids:
            if subshell_id:
                delete_subshell_helper(kc, subshell_id)


@pytest.mark.parametrize("are_subshells", [(False, True), (True, False), (True, True)])
def test_idle_message_parent_headers(are_subshells):
    with new_kernel() as kc:
        # import time module on main shell.
        msg = kc.session.msg("execute_request", {"code": "import time"})
        kc.shell_channel.send(msg)

        subshell_ids = [
            create_subshell_helper(kc)["subshell_id"] if is_subshell else None
            for is_subshell in are_subshells
        ]

        # Wait for all idle status messages to be received.
        for _ in range(1 + sum(are_subshells)):
            wait_for_idle(kc)

        msg_ids = []
        for subshell_id in subshell_ids:
            msg = execute_request(kc, "time.sleep(0.5)", subshell_id)
            msg_ids.append(msg["msg_id"])

        # Expect 4 status messages (2 busy, 2 idle) on iopub channel for the two execute_requests
        statuses = []
        timeout = TIMEOUT  # Combined timeout to receive all the status messages
        t0 = time.time()
        while True:
            status = kc.get_iopub_msg(timeout=timeout)
            if status["msg_type"] != "status" or status["parent_header"]["msg_id"] not in msg_ids:
                continue
            statuses.append(status)
            if len(statuses) == 4:
                break
            t1 = time.time()
            timeout -= t1 - t0
            t0 = t1

        execution_states = Counter(msg["content"]["execution_state"] for msg in statuses)
        assert execution_states["busy"] == 2
        assert execution_states["idle"] == 2

        parent_msg_ids = Counter(msg["parent_header"]["msg_id"] for msg in statuses)
        assert parent_msg_ids[msg_ids[0]] == 2
        assert parent_msg_ids[msg_ids[1]] == 2

        parent_subshell_ids = Counter(msg["parent_header"].get("subshell_id") for msg in statuses)
        assert parent_subshell_ids[subshell_ids[0]] == 2
        assert parent_subshell_ids[subshell_ids[1]] == 2

        # Cleanup
        for subshell_id in subshell_ids:
            if subshell_id:
                delete_subshell_helper(kc, subshell_id)


def test_silent_flag_in_subshells():
    """Verifies that the 'silent' flag suppresses output in main and subshell contexts."""
    with new_kernel() as kc:
        subshell_id = None
        try:
            flush_channels(kc)
            # Test silent execution in main shell
            msg_main_silent = execute_request(kc, "a=1", None, silent=True)
            reply_main_silent = get_reply(kc, msg_main_silent["header"]["msg_id"])
            assert reply_main_silent["content"]["status"] == "ok"

            # Test silent execution in subshell
            subshell_id = create_subshell_helper(kc)["subshell_id"]
            msg_sub_silent = execute_request(kc, "b=2", subshell_id, silent=True)
            reply_sub_silent = get_reply(kc, msg_sub_silent["header"]["msg_id"])
            assert reply_sub_silent["content"]["status"] == "ok"

            # Check for no iopub messages (other than status) from the silent requests
            for msg_id in [msg_main_silent["header"]["msg_id"], msg_sub_silent["header"]["msg_id"]]:
                while True:
                    try:
                        msg = kc.get_iopub_msg(timeout=0.2)
                        if msg["header"]["msg_type"] == "status":
                            continue
                        pytest.fail(
                            f"Silent execution produced unexpected IOPub message: {msg['header']['msg_type']}"
                        )
                    except Empty:
                        break

            # Test concurrent silent and non-silent execution
            msg_silent = execute_request(
                kc, "import time; time.sleep(0.5); c=3", subshell_id, silent=True
            )
            msg_noisy = execute_request(kc, "print('noisy')", None, silent=False)

            # Wait for both replies
            get_replies(kc, [msg_silent["header"]["msg_id"], msg_noisy["header"]["msg_id"]])

            # Verify that we only receive stream output from the noisy message
            stdout, stderr = assemble_output(
                kc.get_iopub_msg, parent_msg_id=msg_noisy["header"]["msg_id"]
            )
            assert "noisy" in stdout
            assert not stderr

            # Verify there is no output from the concurrent silent message
            while True:
                try:
                    msg = kc.get_iopub_msg(timeout=0.2)
                    if (
                        msg["header"]["msg_type"] == "status"
                        and msg["parent_header"].get("msg_id") == msg_silent["header"]["msg_id"]
                    ):
                        continue
                    if msg["parent_header"].get("msg_id") == msg_silent["header"]["msg_id"]:
                        pytest.fail(
                            "Silent execution in concurrent setting produced unexpected IOPub message"
                        )
                except Empty:
                    break
        finally:
            # Ensure subshell is always deleted
            if subshell_id:
                delete_subshell_helper(kc, subshell_id)
