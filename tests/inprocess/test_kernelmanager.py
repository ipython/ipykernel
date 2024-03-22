# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import unittest

import pytest
from anyio import create_task_group
from flaky import flaky

from ipykernel.inprocess.manager import InProcessKernelManager

# -----------------------------------------------------------------------------
# Test case
# -----------------------------------------------------------------------------


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def km_kc(anyio_backend):
    async with create_task_group() as tg:
        km = InProcessKernelManager()
        await tg.start(km.start_kernel)
        kc = km.client()
        kc.start_channels()
        await kc.wait_for_ready()
        yield km, kc
        km.shutdown_kernel()


@pytest.fixture()
async def km(anyio_backend):
    km = InProcessKernelManager()
    yield km
    if km.has_kernel:
        km.shutdown_kernel()


class TestInProcessKernelManager:
    @flaky
    async def test_interface(self, km):
        """Does the in-process kernel manager implement the basic KM interface?"""
        async with create_task_group() as tg:
            assert not km.has_kernel

            await tg.start(km.start_kernel)
            assert km.has_kernel
            assert km.kernel is not None

            kc = km.client()
            assert not kc.channels_running

            kc.start_channels()
            assert kc.channels_running

            old_kernel = km.kernel
            await tg.start(km.restart_kernel)
            assert km.kernel is not None
            assert km.kernel != old_kernel

            km.shutdown_kernel()
            assert not km.has_kernel

            with pytest.raises(NotImplementedError):
                km.interrupt_kernel()

            with pytest.raises(NotImplementedError):
                km.signal_kernel(9)

            kc.stop_channels()
            assert not kc.channels_running

    async def test_execute(self, km_kc):
        """Does executing code in an in-process kernel work?"""
        km, kc = km_kc

        await kc.execute("foo = 1")
        assert km.kernel.shell.user_ns["foo"] == 1

    async def test_complete(self, km_kc):
        """Does requesting completion from an in-process kernel work?"""
        km, kc = km_kc

        km.kernel.shell.push({"my_bar": 0, "my_baz": 1})
        await kc.complete("my_ba", 5)
        msg = kc.get_shell_msg()
        assert msg["header"]["msg_type"] == "complete_reply"
        assert sorted(msg["content"]["matches"]) == ["my_bar", "my_baz"]

    async def test_inspect(self, km_kc):
        """Does requesting object information from an in-process kernel work?"""
        km, kc = km_kc

        km.kernel.shell.user_ns["foo"] = 1
        await kc.inspect("foo")
        msg = kc.get_shell_msg()
        assert msg["header"]["msg_type"] == "inspect_reply"
        content = msg["content"]
        assert content["found"]
        text = content["data"]["text/plain"]
        assert "int" in text

    async def test_history(self, km_kc):
        """Does requesting history from an in-process kernel work?"""
        km, kc = km_kc

        await kc.execute("1")
        await kc.history(hist_access_type="tail", n=1)
        msg = kc.shell_channel.get_msgs()[-1]
        assert msg["header"]["msg_type"] == "history_reply"
        history = msg["content"]["history"]
        assert len(history) == 1
        assert history[0][2] == "1"


if __name__ == "__main__":
    unittest.main()
