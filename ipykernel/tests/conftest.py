import asyncio
import logging
import os

import pytest
import zmq
from jupyter_client.session import Session
from tornado.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from ipykernel.kernelbase import Kernel

try:
    import resource
except ImportError:
    # Windows
    resource = None


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
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class TestKernel(Kernel):
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
    log = logging.getLogger()

    def __init__(self, *args, **kwargs):
        self.context = context = zmq.Context()
        self.iopub_socket = context.socket(zmq.PUB)
        self.session = Session()
        self.test_sockets = [self.iopub_socket]
        self.test_streams = []

        for name in ["shell", "control"]:
            socket = context.socket(zmq.ROUTER)
            stream = ZMQStream(socket)
            stream.on_send(self._on_send)
            self.test_sockets.append(socket)
            self.test_streams.append(stream)
            setattr(self, f"{name}_stream", stream)
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

    async def do_debug_request(self, msg):
        return {}

    async def test_shell_message(self, *args, **kwargs):
        msg_list = self._prep_msg(*args, **kwargs)
        await self.dispatch_shell(msg_list)
        self.shell_stream.flush()
        return await self._wait_for_msg()

    async def test_control_message(self, *args, **kwargs):
        msg_list = self._prep_msg(*args, **kwargs)
        await self.process_control(msg_list)
        self.control_stream.flush()
        return await self._wait_for_msg()

    def destroy(self):
        for stream in self.test_streams:
            stream.close()
        for socket in self.test_sockets:
            socket.close()
        self.context.destroy()

    def _on_send(self, msg, *args, **kwargs):
        self._reply = msg

    def _prep_msg(self, *args, **kwargs):
        self._reply = None
        msg = self.session.msg(*args, **kwargs)
        msg = self.session.serialize(msg)
        return [zmq.Message(m) for m in msg]

    async def _wait_for_msg(self):
        while not self._reply:
            await asyncio.sleep(0.1)
        _, msg = self.session.feed_identities(self._reply)
        return self.session.deserialize(msg)

    def _send_interupt_children(self):
        # override to prevent deadlock
        pass


@pytest.fixture
async def kernel():
    kernel = TestKernel()
    kernel.io_loop = IOLoop.current()
    yield kernel
    kernel.destroy()
