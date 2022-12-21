"""Test subshell"""

import time

from .utils import flush_channels, get_reply, start_new_kernel

KC = KM = None


def setup_function():
    """start the global kernel (if it isn't running) and return its client"""
    global KM, KC
    KM, KC = start_new_kernel()
    flush_channels(KC)


def teardown_function():
    assert KC is not None
    assert KM is not None
    KC.stop_channels()
    KM.shutdown_kernel(now=True)


def test_subshell():
    flush_channels(KC)

    # create sub-shells
    shell_ids = []
    n_subshells = 5
    for _ in range(n_subshells):
        msg = KC.session.msg("create_subshell_request")
        KC.control_channel.send(msg)
        reply = get_reply(KC, msg["header"]["msg_id"], channel="control")
        shell_ids.append(reply["content"]["shell_id"])

    t0 = time.time()
    seconds1 = 1  # main shell execution time
    # will wait some time in main shell
    msg1 = KC.session.msg(
        "execute_request", {"code": f"import time; time.sleep({seconds1})", "silent": False}
    )
    KC.shell_channel.send(msg1)
    msg_ids = []
    seconds = []
    # try running (blocking) code in parallel
    # will wait more time in each sub-shell
    for i, shell_id in enumerate(shell_ids):
        seconds2 = (2 + i * 0.1) * seconds1  # sub-shell execution time
        msg2 = KC.session.msg(
            "execute_request", {"code": f"import time; time.sleep({seconds2})", "silent": False}
        )
        msg2["header"]["shell_id"] = shell_id
        KC.shell_channel.send(msg2)
        seconds.append(seconds2)
        msg_ids.append(msg2["header"]["msg_id"])
    # in any case, main shell should finish first
    reply = get_reply(KC, msg1["header"]["msg_id"])
    dt1 = time.time() - t0
    # main shell execution should not take much more than seconds1
    assert seconds1 < dt1 < seconds1 * 1.1
    # in any case, sub-shells should finish after main shell, an in order
    for i, msg_id in enumerate(msg_ids):
        reply = get_reply(KC, msg_id)
        dt2 = time.time() - t0
        # sub-shell execution should not take much more than seconds2
        assert seconds[i] < dt2 < seconds[i] * 1.1
