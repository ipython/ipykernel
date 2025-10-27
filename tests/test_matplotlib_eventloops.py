import os
import sys
import time

import pytest
from jupyter_client.blocking.client import BlockingKernelClient

from .test_eventloop import qt_guis_avail
from .utils import assemble_output

# these tests don't seem to work with xvfb yet
# these tests seem to be a problem on CI in general
pytestmark = pytest.mark.skipif(
    bool(os.getenv("CI")),
    reason="tests not working yet reliably on CI",
)

guis = []
if not sys.platform.startswith("tk"):
    guis.append("tk")
if qt_guis_avail:
    guis.append("qt")
if sys.platform == "darwin":
    guis.append("osx")

backends = {
    "tk": "tkagg",
    "qt": "qtagg",
    "osx": "macosx",
}


def execute(
    kc: BlockingKernelClient,
    code: str,
    timeout=120,
):
    msg_id = kc.execute(code)
    stdout, stderr = assemble_output(kc.get_iopub_msg, timeout=timeout, parent_msg_id=msg_id)
    assert not stderr.strip()
    return stdout.strip(), stderr.strip()


@pytest.mark.parametrize("gui", guis)
@pytest.mark.timeout(300)
def test_matplotlib_gui(kc, gui):
    """Make sure matplotlib activates and its eventloop runs while the kernel is also responsive"""
    pytest.importorskip("matplotlib", reason="this test requires matplotlib")
    stdout, stderr = execute(kc, f"%matplotlib {gui}")
    assert not stderr
    # debug: show output from invoking the matplotlib magic
    print(stdout)
    execute(
        kc,
        """
    from concurrent.futures import Future
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    """,
    )
    stdout, _ = execute(kc, "print(mpl.get_backend())")
    assert stdout == backends[gui]
    execute(
        kc,
        """
fig, ax = plt.subplots()
timer = fig.canvas.new_timer(interval=10)
f = Future()

call_count = 0
def add_call():
    global call_count
    call_count += 1
    if not f.done():
        f.set_result(None)

timer.add_callback(add_call)
timer.start()
""",
    )
    # wait for the first call (up to 60 seconds)
    deadline = time.monotonic() + 60
    done = False
    while time.monotonic() <= deadline:
        stdout, _ = execute(kc, "print(f.done())")
        if stdout.strip() == "True":
            done = True
            break
        if stdout == "False":
            time.sleep(0.1)
        else:
            pytest.fail(f"Unexpected output {stdout}")
    if not done:
        pytest.fail("future never finished...")

    time.sleep(0.25)
    stdout, _ = execute(kc, "print(call_count)")
    call_count = int(stdout)
    assert call_count > 0
    time.sleep(0.25)
    stdout, _ = execute(kc, "timer.stop()\nprint(call_count)")
    call_count_2 = int(stdout)
    assert call_count_2 > call_count
    stdout, _ = execute(kc, "print(call_count)")
    call_count_3 = int(stdout)
    assert call_count_3 <= call_count_2 + 5
