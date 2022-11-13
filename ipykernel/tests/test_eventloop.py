"""Test eventloop integration"""

import asyncio
import threading
import time

import pytest
import tornado

from ipykernel.eventloops import enable_gui, loop_asyncio, loop_tk

from .utils import execute, flush_channels, start_new_kernel

KC = KM = None


def setup():
    """start the global kernel (if it isn't running) and return its client"""
    global KM, KC
    KM, KC = start_new_kernel()
    flush_channels(KC)


def teardown():
    KC.stop_channels()
    KM.shutdown_kernel(now=True)


async_code = """
from ipykernel.tests._asyncio_utils import async_func
async_func()
"""


@pytest.mark.skipif(tornado.version_info < (5,), reason="only relevant on tornado 5")
def test_asyncio_interrupt():
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


def test_tk_loop(kernel):
    def do_thing():
        time.sleep(1)
        kernel.app_wrapper.app.quit()

    t = threading.Thread(target=do_thing)
    t.start()
    loop_tk(kernel)
    t.join()


def test_asyncio_loop(kernel):
    def do_thing():
        loop.call_soon(loop.stop)

    loop = asyncio.get_event_loop()
    loop.call_soon(do_thing)
    loop_asyncio(kernel)


def test_enable_gui(kernel):
    enable_gui("tk", kernel)
