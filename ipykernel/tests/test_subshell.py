import time
from textwrap import dedent

from jupyter_client.manager import start_new_kernel


def test_subshell():
    km, kc = start_new_kernel()

    shell_id = "foo"
    content = dict(shell_id=shell_id)
    msg = kc.session.msg("subshell_request", content)
    kc.control_channel.send(msg)
    msg = kc.get_control_msg()
    assert msg["content"]["shell_id"] == shell_id

    def get_content(t):
        code = dedent(
            f"""
            import time

            time.sleep({t})
            """
        )
        content = dict(
            code=code,
            silent=False,
        )
        return content

    # launch execution in main shell
    t0 = time.time()
    msg0 = kc.session.msg("execute_request", get_content(0.3))
    kc.shell_channel.send(msg0)

    time.sleep(0.1)

    # launch execution in subshell while main shell is executing
    t1 = time.time()
    metadata = dict(shell_id=shell_id)
    msg1 = kc.session.msg("execute_request", get_content(0.1), metadata=metadata)
    kc.shell_channel.send(msg1)

    msg = kc.get_shell_msg()
    t = time.time()
    # subshell should have finished execution first
    assert msg["parent_header"]["msg_id"] == msg1["msg_id"]
    # subshell execution should take ~0.1s if done in parallel
    assert 0.1 < t - t1 < 0.2

    msg = kc.get_shell_msg()
    t = time.time()
    # main shell shoud have finished execution last
    assert msg["parent_header"]["msg_id"] == msg0["msg_id"]
    # main shell execution should take ~0.3s
    assert 0.3 < t - t0 < 0.4

    kc.stop_channels()
    km.shutdown_kernel()
