"""Regression test for the dual-use shell ROUTER wedge (gh-1529).

ipykernel 7's shell ROUTER is read by a ``ZMQStream`` on the shell-channel thread while
replies are sent back over the *same* socket out-of-band by
``SubshellManager._send_on_shell_channel``. A raw ``send_multipart`` on that socket drains
its edge-triggered ``ZMQ_FD`` read edge; because the stream never sees the send it is never
re-armed, so a request that arrived concurrently can strand unread on a registered-but-
non-readable fd. The kernel then goes idle and never replies -- an intermittent dropped
``execute_request``, most visible on Windows but a generic libzmq edge-trigger behaviour.

This test reproduces the strand *precondition* deterministically -- a request queued on the
ROUTER whose read edge has already been consumed, with the stream not yet having delivered
it -- then performs the out-of-band reply send through the real code path and asserts the
queued request is still delivered to ``on_recv``.

It is deliberately *behavioural*: it checks delivery, not how the fix is implemented, so it
holds whether the reply send re-arms the stream explicitly or is routed through the stream.
Without the fix the queued request is never delivered and the test fails (times out). The
strand precondition is created with documented raw-``zmq`` operations rather than a timing
race, so the test is deterministic. It relies on the libzmq ``ZMQ_FD`` edge-trigger
behaviour, which is documented as general (not Windows-specific); it has been verified here
on Windows, and CI confirms the other platforms.
"""

from __future__ import annotations

import asyncio
import threading
import time

import zmq
from tornado.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from ipykernel.subshell_manager import SubshellManager
from ipykernel.thread import SHELL_CHANNEL_THREAD_NAME

TIMEOUT = 10.0


def _run_on_loop(loop, func):
    """Run ``func()`` on the loop thread, block until it finishes, return/raise its result."""
    box: dict = {}
    done = threading.Event()

    def runner():
        try:
            box["result"] = func()
        except BaseException as exc:
            box["error"] = exc
        finally:
            done.set()

    loop.add_callback(runner)
    if not done.wait(TIMEOUT):
        msg = "callback did not complete on the shell-channel loop"
        raise TimeoutError(msg)
    if "error" in box:
        raise box["error"]
    return box.get("result")


def test_concurrent_request_not_stranded_by_reply_send():
    context = zmq.Context()

    # Shell ROUTER, read by a ZMQStream on the shell-channel loop -- exactly like the kernel.
    shell_socket = context.socket(zmq.ROUTER)
    port = shell_socket.bind_to_random_port("tcp://127.0.0.1")

    client = context.socket(zmq.DEALER)
    client.setsockopt(zmq.IDENTITY, b"client-1")
    client.connect(f"tcp://127.0.0.1:{port}")

    # An IOLoop in a thread named like the kernel's shell-channel thread: the
    # _send_on_shell_channel assert requires this exact thread name.
    loop_box: dict = {}
    loop_ready = threading.Event()

    def run_loop():
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = IOLoop.current()
        loop_box["loop"] = loop
        loop.add_callback(loop_ready.set)
        loop.start()

    thread = threading.Thread(target=run_loop, name=SHELL_CHANNEL_THREAD_NAME, daemon=True)
    thread.start()
    assert loop_ready.wait(TIMEOUT), "shell-channel loop did not start"
    loop = loop_box["loop"]

    received: list[list[bytes]] = []
    got_message = threading.Event()
    stream = manager = None

    try:
        # Build the shell stream and manager on the loop thread (add_handler must run there).
        def setup():
            _stream = ZMQStream(shell_socket, loop)

            def on_recv(frames):
                received.append(frames)
                got_message.set()

            _stream.on_recv(on_recv, copy=True)
            _manager = SubshellManager(context, loop, shell_socket, _stream)
            return _stream, _manager

        stream, manager = _run_on_loop(loop, setup)

        # Warmup: teach the ROUTER the client's route and let the stream drain to idle.
        client.send_multipart([b"warmup"])
        assert got_message.wait(TIMEOUT), "warmup request never delivered"
        routing_id = received[0][0]
        assert routing_id == b"client-1"

        received.clear()
        got_message.clear()

        def strand_then_reply():
            # Runs on the loop thread, so the stream's fd handler cannot interleave while
            # this callback executes -- that is what makes the strand deterministic.
            client.send_multipart([b"req-1"])

            # Wait until the request is actually queued on the ROUTER. Reading EVENTS here
            # also consumes the edge-triggered read edge (libzmq ZMQ_FD corollary), so by
            # the time we exit this loop the request is queued and unread while the fd is
            # no longer readable -- the coalesced-edge strand precondition.
            deadline = time.monotonic() + TIMEOUT
            while not (shell_socket.events & zmq.POLLIN):
                if time.monotonic() > deadline:
                    msg = "request never queued on the ROUTER"
                    raise TimeoutError(msg)

            assert not got_message.is_set(), "request delivered before the reply send"

            # Out-of-band reply send through the real code path. With the fix this re-arms /
            # routes through the stream so the queued request is serviced; without it the
            # request stays stranded on the registered-but-non-readable fd.
            manager._send_on_shell_channel([routing_id, b"reply"])

        _run_on_loop(loop, strand_then_reply)

        assert got_message.wait(TIMEOUT), (
            "the concurrently-queued request was stranded by the out-of-band reply send "
            "and never delivered to on_recv -- the shell-channel wedge has regressed"
        )
        assert received and received[-1][-1] == b"req-1"
    finally:

        def teardown():
            if manager is not None:
                try:
                    manager.close()
                except Exception:
                    pass
            if stream is not None:
                stream.close()

        try:
            _run_on_loop(loop, teardown)
        except Exception:
            pass
        loop.add_callback(loop.stop)
        thread.join(timeout=TIMEOUT)
        client.close()
        shell_socket.close()
        context.term()
