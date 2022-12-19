"""Test eventloop integration"""

import asyncio
import os
import sys
import threading
import time

import pytest
import tornado

from ipykernel.eventloops import (
    enable_gui,
    loop_asyncio,
    loop_cocoa,
    loop_tk,
    set_qt_api_env_from_gui,
)

from .utils import execute, flush_channels, start_new_kernel

KC = KM = None

guis_avail = []


def _get_qt_vers():
    for gui in ['qt', 'qt6', 'qt5', 'qt4']:
        try:
            set_qt_api_env_from_gui(gui)
            guis_avail.append(gui)
            if 'QT_API' in os.environ.keys():
                del os.environ['QT_API']
        except ImportError:
            pass  # that version of Qt isn't available.


_get_qt_vers()


def setup():
    """start the global kernel (if it isn't running) and return its client"""
    global KM, KC
    KM, KC = start_new_kernel()
    flush_channels(KC)


def teardown():
    assert KM is not None
    assert KC is not None
    KC.stop_channels()
    KM.shutdown_kernel(now=True)


async_code = """
from ipykernel.tests._asyncio_utils import async_func
async_func()
"""


@pytest.mark.skipif(tornado.version_info < (5,), reason="only relevant on tornado 5")
def test_asyncio_interrupt():
    assert KM is not None
    assert KC is not None
    flush_channels(KC)
    msg_id, content = execute("%gui asyncio", KC)
    assert content["status"] == "ok", content

    flush_channels(KC)
    msg_id, content = execute(async_code, KC)
    assert content["status"] == "ok", content

    KM.interrupt_kernel()

    flush_channels(KC)
    msg_id, content = execute(async_code, KC)
    assert content["status"] == "ok"


windows_skip = pytest.mark.skipif(os.name == "nt", reason="causing failures on windows")


@pytest.mark.skipif(sys.platform == "darwin", reason="hangs on macos")
def test_tk_loop(kernel):
    def do_thing():
        time.sleep(1)
        try:
            kernel.app_wrapper.app.quit()
        # guard for tk failing to start (if there is no display)
        except AttributeError:
            pass

    t = threading.Thread(target=do_thing)
    t.start()
    # guard for tk failing to start (if there is no display)
    try:
        loop_tk(kernel)
    except Exception:
        pass
    t.join()


def test_asyncio_loop(kernel):
    def do_thing():
        loop.call_soon(loop.stop)

    loop = asyncio.get_event_loop()
    loop.call_soon(do_thing)
    loop_asyncio(kernel)


def test_enable_gui(kernel):
    enable_gui("tk", kernel)


@pytest.mark.skipif(sys.platform != "darwin", reason="MacOS-only")
def test_cocoa_loop(kernel):
    loop_cocoa(kernel)


@pytest.mark.skipif(len(guis_avail) == 0, reason='No viable version of PyQt or PySide installed.')
def test_qt_enable_gui(kernel):
    gui = guis_avail[0]

    enable_gui(gui, kernel)

    # This tags the kernel with the gui that was requested:
    assert kernel.last_qt_version == gui

    # We store the `QApplication` instance in the kernel.
    assert hasattr(kernel, 'app')
    # And the `QEventLoop` is added to `app`:`
    assert hasattr(kernel.app, 'qt_event_loop')

    # Can't start another event loop, even if `gui` is the same.
    with pytest.raises(RuntimeError):
        enable_gui(gui, kernel)

    # Turning off the event loop retains `last_qt_version`; now we're stuck importing that forever.
    enable_gui(None, kernel)
    assert kernel.last_qt_version == gui
    assert not hasattr(kernel, 'app')

    if len(guis_avail) > 1:
        for gui2 in guis_avail[1:]:
            # Won't work; Qt version is different than the first one.
            with pytest.raises(ValueError):
                enable_gui(gui2, kernel)

    # A gui of 'qt' means "latest availble", or in this case, the last one that was used.
    enable_gui('qt', kernel)
