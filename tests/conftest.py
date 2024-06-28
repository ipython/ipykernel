import asyncio
import logging
import os
from math import inf
from typing import Any, Callable, no_type_check
from unittest.mock import MagicMock

import pytest
import zmq
import zmq.asyncio
from anyio import create_memory_object_stream, create_task_group
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from jupyter_client.session import Session

from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelbase import Kernel
from ipykernel.zmqshell import ZMQInteractiveShell

try:
    import resource
except ImportError:
    # Windows
    resource = None  # type:ignore


@pytest.fixture()
def anyio_backend():
    return "asyncio"


pytestmark = pytest.mark.anyio


# Handle resource limit
# Ensure a minimal soft limit of DEFAULT_SOFT if the current hard limit is at least that much.
if resource is not None:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)

    DEFAULT_SOFT = 4096
    if hard >= DEFAULT_SOFT:
        soft = DEFAULT_SOFT

    if hard < soft:
        hard = soft

    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))


# Enforce selector event loop on Windows.
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type:ignore


class TestSession(Session):
    """A session that copies sent messages to an internal stream, so that
    they can be accessed later.
    """

    def __init__(self, sockets, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._streams = {}
        for socket in sockets:
            send_stream, receive_stream = create_memory_object_stream(max_buffer_size=inf)
            self._streams[socket] = {"send": send_stream, "receive": receive_stream}

    def close(self):
        for streams in self._streams.values():
            for stream in streams.values():
                stream.close()
        self._streams.clear()

    def send(self, socket, *args, **kwargs):
        msg = super().send(socket, *args, **kwargs)
        send_stream: MemoryObjectSendStream[Any] = self._streams[socket]["send"]
        send_stream.send_nowait(msg)
        return msg


class KernelMixin:
    shell_socket: zmq.asyncio.Socket
    control_socket: zmq.asyncio.Socket
    stop: Callable[[], None]

    log = logging.getLogger()

    def _initialize(self):
        self._is_test = True
        self.context = context = zmq.asyncio.Context()
        self.iopub_socket = context.socket(zmq.PUB)
        self.stdin_socket = context.socket(zmq.ROUTER)
        self.test_sockets = [self.iopub_socket]

        for name in ["shell", "control"]:
            socket = context.socket(zmq.ROUTER)
            self.test_sockets.append(socket)
            setattr(self, f"{name}_socket", socket)

        self.session = TestSession(
            [
                self.shell_socket,
                self.control_socket,
                self.iopub_socket,
            ]
        )

    async def do_debug_request(self, msg):
        return {}

    def destroy(self):
        self.stop()
        self.session.close()
        for socket in self.test_sockets:
            socket.close()
        self.context.destroy()

    @no_type_check
    async def test_shell_message(self, *args, **kwargs):
        msg_list = self._prep_msg(*args, **kwargs)
        await self.process_shell_message(msg_list)
        receive_stream: MemoryObjectReceiveStream[Any] = self.session._streams[self.shell_socket][
            "receive"
        ]
        return await receive_stream.receive()

    @no_type_check
    async def test_control_message(self, *args, **kwargs):
        msg_list = self._prep_msg(*args, **kwargs)
        await self.process_control_message(msg_list)
        receive_stream: MemoryObjectReceiveStream[Any] = self.session._streams[self.control_socket][
            "receive"
        ]
        return await receive_stream.receive()

    def _on_send(self, msg, *args, **kwargs):
        self._reply = msg

    def _prep_msg(self, *args, **kwargs):
        self._reply = None
        raw_msg = self.session.msg(*args, **kwargs)
        msg = self.session.serialize(raw_msg)
        return msg

    async def _wait_for_msg(self):
        while not self._reply:
            await asyncio.sleep(0.1)
        _, msg = self.session.feed_identities(self._reply)
        return self.session.deserialize(msg)

    def _send_interrupt_children(self):
        # override to prevent deadlock
        pass


class MockKernel(KernelMixin, Kernel):  # type:ignore
    implementation = "test"
    implementation_version = "1.0"
    language = "no-op"
    language_version = "0.1"
    language_info = {
        "name": "test",
        "mimetype": "text/plain",
        "file_extension": ".txt",
    }
    banner = "test kernel"

    def __init__(self, *args, **kwargs):
        self._initialize()
        self.shell = MagicMock()
        super().__init__(*args, **kwargs)

    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        if not silent:
            stream_content = {"name": "stdout", "text": code}
            self.send_response(self.iopub_socket, "stream", stream_content)

        return {
            "status": "ok",
            # The base class increments the execution count
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }


class MockIPyKernel(KernelMixin, IPythonKernel):  # type:ignore
    def __init__(self, *args, **kwargs):
        self._initialize()
        super().__init__(*args, **kwargs)


@pytest.fixture()
async def kernel(anyio_backend):
    async with create_task_group() as tg:
        kernel = MockKernel()
        tg.start_soon(kernel.start)
        yield kernel
        kernel.destroy()


@pytest.fixture()
async def ipkernel(anyio_backend):
    async with create_task_group() as tg:
        kernel = MockIPyKernel()
        tg.start_soon(kernel.start)
        yield kernel
        kernel.destroy()
        ZMQInteractiveShell.clear_instance()
