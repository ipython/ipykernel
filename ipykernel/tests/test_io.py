"""Test IO capturing functionality"""

import io

import zmq

import pytest

from jupyter_client.session import Session
from ipykernel.iostream import IOPubThread, OutStream


def test_io_api():
    """Test that wrapped stdout has the same API as a normal TextIO object"""
    session = Session()
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    thread = IOPubThread(pub)
    thread.start()

    stream = OutStream(session, thread, 'stdout')

    # cleanup unused zmq objects before we start testing
    thread.stop()
    thread.close()
    ctx.term()

    assert stream.errors is None
    assert not stream.isatty()
    with pytest.raises(io.UnsupportedOperation):
        stream.detach()
    with pytest.raises(io.UnsupportedOperation):
        next(stream)
    with pytest.raises(io.UnsupportedOperation):
        stream.read()
    with pytest.raises(io.UnsupportedOperation):
        stream.readline()
    with pytest.raises(io.UnsupportedOperation):
        stream.seek(0)
    with pytest.raises(io.UnsupportedOperation):
        stream.tell()
    with pytest.raises(TypeError):
        stream.write(b'')

def test_io_isatty():
    session = Session()
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    thread = IOPubThread(pub)
    thread.start()

    stream = OutStream(session, thread, 'stdout', isatty=True)
    assert stream.isatty()
