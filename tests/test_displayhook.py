"""Tests for the ZMQ execute_result displayhook."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import unittest
from queue import Queue
from threading import Thread

import zmq
from IPython.core.interactiveshell import InteractiveShell
from jupyter_client.session import Session
from traitlets import Int

from ipykernel.displayhook import ZMQShellDisplayHook


class NoReturnHook:
    call_count = 0

    def __call__(self, msg):
        self.call_count += 1


class ReturnHook(NoReturnHook):
    def __call__(self, msg):
        super().__call__(msg)
        return msg


class MutatingHook(NoReturnHook):
    """Attaches a buffer to the message and returns it."""

    def __call__(self, msg):
        super().__call__(msg)
        msg.setdefault("buffers", []).append(b"arrow-bytes")
        return msg


class CounterSession(Session):
    send_count = Int(0)
    last_msg = None

    def send(self, *args, **kwargs):
        self.send_count += 1
        # args: (stream, msg_or_type, ...)
        if len(args) >= 2:
            self.last_msg = args[1]
        return super().send(*args, **kwargs)


def _drive(hook, data=None):
    """Run a single execute_result emission through the hook."""
    if data is None:
        data = {"text/plain": "1"}
    hook.start_displayhook()
    hook.write_format_data(data, {})
    hook.finish_displayhook()


class ZMQShellDisplayHookTests(unittest.TestCase):
    def setUp(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.session = CounterSession()
        self.shell = InteractiveShell()
        self.disp = ZMQShellDisplayHook(shell=self.shell)
        self.disp.session = self.session
        self.disp.pub_socket = self.socket

    def tearDown(self):
        self.socket.close()
        self.context.term()

    def test_no_hooks_sends_message(self):
        """With no hooks registered, finish_displayhook still calls send."""
        assert self.disp._hooks == []
        _drive(self.disp)
        assert self.session.send_count == 1

    def test_thread_local_hooks(self):
        """_hooks is thread-local: registering on one thread doesn't leak."""
        assert self.disp._hooks == []

        def hook(msg):
            return msg

        self.disp.register_hook(hook)
        assert self.disp._hooks == [hook]

        q: Queue = Queue()

        def read_other_thread():
            q.put(self.disp._hooks)

        t = Thread(target=read_other_thread)
        t.start()
        other = q.get(timeout=10)
        t.join()
        assert other == []

    def test_hook_returning_none_halts_send(self):
        """A hook that returns None suppresses session.send."""
        hook = NoReturnHook()
        self.disp.register_hook(hook)

        _drive(self.disp)

        assert hook.call_count == 1
        assert self.session.send_count == 0
        assert self.disp.msg is None

    def test_hook_returning_msg_calls_send(self):
        """A hook that returns the message lets it through to send."""
        hook = ReturnHook()
        self.disp.register_hook(hook)

        _drive(self.disp)

        assert hook.call_count == 1
        assert self.session.send_count == 1

    def test_hook_can_mutate_message(self):
        """A hook can attach buffers (the original motivation)."""
        hook = MutatingHook()
        self.disp.register_hook(hook)

        _drive(self.disp)

        assert hook.call_count == 1
        assert self.session.send_count == 1
        sent = self.session.last_msg
        assert sent is not None
        assert sent.get("buffers") == [b"arrow-bytes"]

    def test_hook_chain_short_circuits(self):
        """If an early hook returns None, later hooks are not called."""
        first = NoReturnHook()
        second = NoReturnHook()
        self.disp.register_hook(first)
        self.disp.register_hook(second)

        _drive(self.disp)

        assert first.call_count == 1
        assert second.call_count == 0
        assert self.session.send_count == 0

    def test_hook_chain_threads_message(self):
        """Each hook receives the message returned by the previous hook."""
        observed: list[dict] = []

        def first(msg):
            msg["content"]["metadata"]["seen_by_first"] = True
            return msg

        def second(msg):
            observed.append(msg)
            return msg

        self.disp.register_hook(first)
        self.disp.register_hook(second)

        _drive(self.disp)

        assert len(observed) == 1
        assert observed[0]["content"]["metadata"].get("seen_by_first") is True
        assert self.session.send_count == 1

    def test_unregister_hook(self):
        """Unregistered hooks no longer run; double-unregister returns False."""
        hook = NoReturnHook()
        self.disp.register_hook(hook)

        _drive(self.disp)
        assert hook.call_count == 1
        assert self.session.send_count == 0

        first = self.disp.unregister_hook(hook)
        assert bool(first)

        _drive(self.disp)
        # Hook didn't run again, but the message went out via session.send.
        assert hook.call_count == 1
        assert self.session.send_count == 1

        # Unregistering an unknown hook returns False.
        assert not bool(self.disp.unregister_hook(hook))

    def test_empty_data_skips_send_and_hooks(self):
        """The existing guard: if content.data is empty, don't send or hook."""
        hook = ReturnHook()
        self.disp.register_hook(hook)

        # start_displayhook initializes self.msg with empty data; if we never
        # call write_format_data, the data dict stays empty and finish should
        # short-circuit before calling either hooks or send.
        self.disp.start_displayhook()
        self.disp.finish_displayhook()

        assert hook.call_count == 0
        assert self.session.send_count == 0
        assert self.disp.msg is None


if __name__ == "__main__":
    unittest.main()
