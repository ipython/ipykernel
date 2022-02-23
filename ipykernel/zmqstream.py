import asyncio
from inspect import isawaitable


class ZMQStream:
    def __init__(self, socket, io_loop=None):
        self.socket = socket
        if io_loop is None:
            self.io_loop = asyncio.get_event_loop()
            self.is_thread = False
        else:
            self.io_loop = io_loop
            self.is_thread = True

    def on_recv(self, callback, copy=True):
        if self.is_thread:
            # it is a loop in another thread
            asyncio.run_coroutine_threadsafe(self.recv_task(callback, copy), self.io_loop)
        else:
            # it is the main thread's loop, schedule the task to launch when the loop runs
            asyncio.ensure_future(self.recv_task(callback, copy))

    async def recv_task(self, callback, copy):
        while True:
            msg_list = self.socket.recv_multipart(copy=copy)
            if isawaitable(msg_list):
                # in-process kernels are not async
                msg_list = await msg_list
            callback(msg_list)

    def send_multipart(self, msg_list, flags=0, copy=True, track=False, **kwargs):
        return self.socket.send_multipart(msg_list, copy=copy)

    def flush(self, flag=None, limit=None):
        pass
