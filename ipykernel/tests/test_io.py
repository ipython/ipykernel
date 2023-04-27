"""Test IO capturing functionality"""

import io
import os
import sys
import warnings
from unittest import mock

import pytest
import zmq
from jupyter_client.session import Session

from ipykernel.iostream import MASTER, BackgroundSocket, IOPubThread, OutStream


@pytest.fixture
def ctx():
    ctx = zmq.Context()
    return ctx
    # yield ctx
    ctx.destroy()


@pytest.fixture
def iopub_thread(ctx):
    with ctx.socket(zmq.PUB) as pub:
        thread = IOPubThread(pub)
        thread.start()

        yield thread
        thread.stop()
        thread.close()


def test_io_api(iopub_thread):
    """Test that wrapped stdout has the same API as a normal TextIO object"""
    session = Session()
    stream = OutStream(session, iopub_thread, "stdout")

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
        stream.write(b"")  # type:ignore


def test_io_isatty(iopub_thread):
    session = Session()
    stream = OutStream(session, iopub_thread, "stdout", isatty=True)
    assert stream.isatty()


def test_io_thread(iopub_thread):
    thread = iopub_thread
    thread._setup_pipe_in()
    msg = [thread._pipe_uuid, b"a"]
    thread._handle_pipe_msg(msg)
    ctx1, pipe = thread._setup_pipe_out()
    pipe.close()
    thread._pipe_in.close()
    thread._check_mp_mode = lambda: MASTER  # type:ignore
    thread._really_send([b"hi"])
    ctx1.destroy()
    thread.close()
    thread.close()
    thread._really_send(None)


def test_background_socket(iopub_thread):
    sock = BackgroundSocket(iopub_thread)
    assert sock.__class__ == BackgroundSocket
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        sock.linger = 101
        assert iopub_thread.socket.linger == 101
    assert sock.io_thread == iopub_thread
    sock.send(b"hi")


def test_outstream(iopub_thread):
    session = Session()
    pub = iopub_thread.socket
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        stream = OutStream(session, pub, "stdout")
        stream.close()
        stream = OutStream(session, iopub_thread, "stdout", pipe=object())
        stream.close()

        stream = OutStream(session, iopub_thread, "stdout", watchfd=False)
        stream.close()

    stream = OutStream(session, iopub_thread, "stdout", isatty=True, echo=io.StringIO())

    with stream:
        with pytest.raises(io.UnsupportedOperation):
            stream.fileno()
        stream._watch_pipe_fd()
        stream.flush()
        stream.write("hi")
        stream.writelines(["ab", "cd"])
        assert stream.writable()


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Windows")
def test_echo_watch(capfd, iopub_thread):
    """Test echo on underlying FD while capturing the same FD

    If not careful, this
    """
    session = Session()

    stdout_fd = sys.stdout.fileno()
    stream = OutStream(
        session,
        iopub_thread,
        "stdout",
        isatty=True,
        echo=sys.stdout,
    )
    save_stdout = sys.stdout
    with stream, mock.patch.object(sys, "stdout", stream):
        # write to low-level FD
        os.write(stdout_fd, b"fd\n")
        os.fsync(stdout_fd)
        # write to unwrapped __stdout__ (should also go to original FD)
        sys.__stdout__.write("__stdout__\n")
        sys.__stdout__.flush()
        # write to original sys.stdout (should be the same as __stdout__)
        save_stdout.write("stdout\n")
        save_stdout.flush()
        # print (writes to stream)
        print("print")
        sys.stdout.flush()

    out, err = capfd.readouterr()
    print(out, err)
    assert out.strip() == "fd\n__stdout__\nstdout\nprint"
