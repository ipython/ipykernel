import os
from textwrap import dedent

import pytest
from flaky import flaky

from .test_embed_kernel import setup_kernel

TIMEOUT = 15

if os.name == "nt":
    pytest.skip("skipping tests on windows", allow_module_level=True)


@flaky(max_runs=3)
def test_ipython_start_kernel_userns():
    cmd = dedent(
        """
        from ipykernel.kernelapp import launch_new_instance
        ns = {"tre": 123}
        launch_new_instance(user_ns=ns)
        """
    )

    with setup_kernel(cmd) as client:
        client.inspect("tre")
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["found"]
        text = content["data"]["text/plain"]
        assert "123" in text

        # user_module should be an instance of DummyMod
        client.execute("usermod = get_ipython().user_module")
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["status"] == "ok"
        client.inspect("usermod")
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["found"]
        text = content["data"]["text/plain"]
        assert "DummyMod" in text


@flaky(max_runs=3)
def test_ipython_start_kernel_no_userns():
    # Issue #4188 - user_ns should be passed to shell as None, not {}
    cmd = dedent(
        """
        from ipykernel.kernelapp import launch_new_instance
        launch_new_instance()
        """
    )

    with setup_kernel(cmd) as client:
        # user_module should not be an instance of DummyMod
        client.execute("usermod = get_ipython().user_module")
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["status"] == "ok"
        client.inspect("usermod")
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["found"]
        text = content["data"]["text/plain"]
        assert "DummyMod" not in text


@flaky(max_runs=3)
async def test_ipython_kernel_multiprocessing(capsys):
    cmd = dedent(
        """
        from ipykernel.kernelapp import launch_new_instance
        launch_new_instance()
        """
    )
    code = 'import multiprocessing as mp;import time;p = mp.get_context("spawn").Process(target=time.sleep, args=(0.1,));p.start()'
    with setup_kernel(cmd) as client:
        client.execute(code)
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["status"] == "ok"
        while True:
            msg = client.get_iopub_msg(timeout=TIMEOUT)
            if msg['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                break
