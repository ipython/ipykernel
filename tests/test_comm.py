import unittest.mock

import pytest

from ipykernel.comm import Comm, CommManager
from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelbase import Kernel


def test_comm(kernel: Kernel) -> None:
    manager = CommManager(kernel=kernel)
    kernel.comm_manager = manager  # type:ignore

    with pytest.deprecated_call():
        c = Comm(kernel=kernel, target_name="bar")
    msgs = []

    assert kernel is c.kernel  # type:ignore

    def on_close(msg):
        msgs.append(msg)

    def on_message(msg):
        msgs.append(msg)

    c.publish_msg("foo")
    c.open({})
    c.on_msg(on_message)
    c.on_close(on_close)
    c.handle_msg({})
    c.handle_close({})
    c.close()
    assert len(msgs) == 2
    assert c.target_name == "bar"


def test_comm_manager(kernel: Kernel) -> None:
    manager = CommManager(kernel=kernel)
    msgs = []

    def foo(comm, msg):
        msgs.append(msg)
        comm.close()

    def fizz(comm, msg):
        raise RuntimeError("hi")

    def on_close(msg):
        msgs.append(msg)

    def on_msg(msg):
        msgs.append(msg)

    manager.register_target("foo", foo)
    manager.register_target("fizz", fizz)

    kernel.comm_manager = manager  # type:ignore
    with unittest.mock.patch.object(Comm, "publish_msg") as publish_msg:
        with pytest.deprecated_call():
            comm = Comm()
        comm.on_msg(on_msg)
        comm.on_close(on_close)
        manager.register_comm(comm)
        assert publish_msg.call_count == 1

    # make sure that when we don't pass a kernel, the 'default' kernel is taken
    Kernel._instance = kernel  # type:ignore
    assert comm.kernel is kernel  # type:ignore
    Kernel.clear_instance()

    assert manager.get_comm(comm.comm_id) == comm
    assert manager.get_comm("foo") is None

    msg = dict(content=dict(comm_id=comm.comm_id, target_name="foo"))
    manager.comm_open(None, None, msg)
    assert len(msgs) == 1
    msg["content"]["target_name"] = "bar"
    manager.comm_open(None, None, msg)
    assert len(msgs) == 1
    msg = dict(content=dict(comm_id=comm.comm_id, target_name="fizz"))
    manager.comm_open(None, None, msg)
    assert len(msgs) == 1

    manager.register_comm(comm)
    assert manager.get_comm(comm.comm_id) == comm
    msg = dict(content=dict(comm_id=comm.comm_id))
    manager.comm_msg(None, None, msg)
    assert len(msgs) == 2
    msg["content"]["comm_id"] = "foo"
    manager.comm_msg(None, None, msg)
    assert len(msgs) == 2

    manager.register_comm(comm)
    assert manager.get_comm(comm.comm_id) == comm
    msg = dict(content=dict(comm_id=comm.comm_id))
    manager.comm_close(None, None, msg)
    assert len(msgs) == 3

    assert comm._closed


def test_comm_in_manager(ipkernel: IPythonKernel) -> None:
    with pytest.deprecated_call():
        comm = Comm()

    assert comm.comm_id in ipkernel.comm_manager.comms


def test_handle_msg_skips_events_when_dispatched_concurrently(
    kernel: Kernel, monkeypatch: pytest.MonkeyPatch
) -> None:
    """handle_msg must not fire pre/post_execute for a concurrently dispatched comm.

    Regression test for ipython/ipykernel#1564: when a comm_msg is dispatched
    while an async cell holds the shell lock, its callback runs under the
    comm_msg's parent header, so output a post_execute hook publishes would be
    parented to the comm_msg and dropped by frontends.
    """
    Kernel._instance = kernel  # type: ignore[attr-defined]
    try:
        events: list[str] = []
        shell = unittest.mock.Mock()
        shell.events.trigger.side_effect = lambda name: events.append(name)
        monkeypatch.setattr("IPython.get_ipython", lambda: shell)
        with pytest.deprecated_call():
            comm = Comm(kernel=kernel, target_name="test")
        comm.on_msg(lambda msg: events.append("callback"))

        token = kernel._in_concurrent_comm_dispatch.set(True)
        try:
            comm.handle_msg({})
        finally:
            kernel._in_concurrent_comm_dispatch.reset(token)
        assert events == ["callback"]

        events.clear()
        comm.handle_msg({})
        assert events == ["pre_execute", "callback", "post_execute"]
    finally:
        Kernel.clear_instance()
