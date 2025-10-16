import os
from textwrap import dedent

import pytest

from .test_embed_kernel import setup_kernel

TIMEOUT = 15

if os.name == "nt":
    pytest.skip("skipping tests on windows", allow_module_level=True)


@pytest.mark.flaky(max_runs=3)
def test_ipython_start_kernel_userns():
    import IPython

    if IPython.version_info > (9, 0):  # noqa:SIM108
        EXPECTED = "IPythonMainModule"
    else:
        # not this since https://github.com/ipython/ipython/pull/14754
        EXPECTED = "DummyMod"

    cmd = dedent(
        """
        from ipykernel.kernelapp import launch_new_instance
        ns = {"custom": 123}
        launch_new_instance(user_ns=ns)
        """
    )

    with setup_kernel(cmd) as client:
        client.inspect("custom")
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
        assert EXPECTED in text


def test_start_kernel_background_thread():
    cmd = dedent(
        """
        import threading
        import asyncio
        from ipykernel.kernelapp import launch_new_instance

        def launch():
            # Threads don't always have a default event loop so we need to
            # create and set a default
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            launch_new_instance()

        thread = threading.Thread(target=launch)
        thread.start()
        thread.join()
        """
    )

    with setup_kernel(cmd) as client:
        client.execute("a = 1")
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["status"] == "ok"

        client.inspect("a")
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg["content"]
        assert content["found"]
        text = content["data"]["text/plain"]
        assert "1" in text


@pytest.mark.flaky(max_runs=3)
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
