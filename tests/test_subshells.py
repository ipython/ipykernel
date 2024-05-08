"""Test kernel subshells."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from .utils import TIMEOUT, get_reply, kernel


# Helpers

def create_subshell_helper(kc):
    msg = kc.session.msg("create_subshell_request")
    kc.control_channel.send(msg)
    msg_id = msg["header"]["msg_id"]
    reply = get_reply(kc, msg_id, TIMEOUT, channel="control")
    return reply["content"]


def delete_subshell_helper(kc, subshell_id):
    msg = kc.session.msg("delete_subshell_request", {"subshell_id": subshell_id})
    kc.control_channel.send(msg)
    msg_id = msg["header"]["msg_id"]
    reply = get_reply(kc, msg_id, TIMEOUT, channel="control")
    return reply["content"]


def list_subshell_helper(kc):
    msg = kc.session.msg("list_subshell_request")
    kc.control_channel.send(msg)
    msg_id = msg["header"]["msg_id"]
    reply = get_reply(kc, msg_id, TIMEOUT, channel="control")
    return reply["content"]


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
