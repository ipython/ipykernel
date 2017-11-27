"""Test eventloop integration"""

import sys
import time

import IPython.testing.decorators as dec
from .utils import flush_channels, start_new_kernel, execute

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
from ipykernel.tests._asyncio import async_func
async_func()
"""


@dec.skipif(sys.version_info < (3, 5), "async/await syntax required")
def test_asyncio_interrupt():
    flush_channels(KC)
    msg_id, content = execute('%gui asyncio', KC)
    assert content['status'] == 'ok', content

    flush_channels(KC)
    msg_id, content = execute(async_code, KC)
    assert content['status'] == 'ok', content

    KM.interrupt_kernel()

    flush_channels(KC)
    msg_id, content = execute(async_code, KC)
    assert content['status'] == 'ok'
