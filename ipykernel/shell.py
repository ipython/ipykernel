import asyncio
import inspect
import sys
from threading import Thread

import zmq

if zmq.pyzmq_version_info() >= (17, 0):
    from tornado.ioloop import IOLoop
else:
    # deprecated since pyzmq 17
    from zmq.eventloop.ioloop import IOLoop


async def handle_message(idents, msg, kernel, is_main):
    if is_main:
        # Set the parent message for side effects.
        kernel.set_parent(idents, msg, channel="shell")
        kernel._publish_status("busy", "shell")

    msg_type = msg["header"]["msg_type"]

    # Only abort execute requests
    if kernel._aborting and msg_type == "execute_request":
        kernel._send_abort_reply(kernel.shell_stream, msg, idents)
        kernel._publish_status("idle", "shell")
        # flush to ensure reply is sent before
        # handling the next request
        kernel.shell_stream.flush(zmq.POLLOUT)
        return

    # Print some info about this message and leave a '--->' marker, so it's
    # easier to trace visually the message chain when debugging.  Each
    # handler prints its message at the end.
    kernel.log.debug("\n*** MESSAGE TYPE:%s***", msg_type)
    kernel.log.debug("   Content: %s\n   --->\n   ", msg["content"])

    if not kernel.should_handle(kernel.shell_stream, msg, idents):
        return

    handler = kernel.shell_handlers.get(msg_type, None)
    if handler is None:
        kernel.log.warning("Unknown message type: %r", msg_type)
    else:
        kernel.log.debug("%s: %s", msg_type, msg)
        try:
            kernel.pre_handler_hook()
        except Exception:
            kernel.log.debug("Unable to signal in pre_handler_hook:", exc_info=True)
        try:
            result = handler(kernel.shell_stream, idents, msg)
            if inspect.isawaitable(result):
                await result
        except Exception:
            kernel.log.error("Exception in message handler:", exc_info=True)
        except KeyboardInterrupt:
            # Ctrl-c shouldn't crash the kernel here.
            kernel.log.error("KeyboardInterrupt caught in kernel.")
        finally:
            try:
                kernel.post_handler_hook()
            except Exception:
                kernel.log.debug("Unable to signal in post_handler_hook:", exc_info=True)

        if is_main:
            sys.stdout.flush()
            sys.stderr.flush()
            kernel._publish_status("idle", "shell")

        # flush to ensure reply is sent before
        # handling the next request
        kernel.shell_stream.flush(zmq.POLLOUT)


async def handle_messages(msg_queue, kernel, is_main):
    while True:
        res = msg_queue.get()
        if is_main:
            res = await res
        idents, msg = res
        await handle_message(idents, msg, kernel, is_main)


class SubshellThread(Thread):
    def __init__(self, shell_id, msg_queue, kernel):
        self.msg_queue = msg_queue
        self.kernel = kernel
        super().__init__(name=f"Subshell_{shell_id}", daemon=True)

    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(handle_messages(self.msg_queue, self.kernel, False))


class ShellThread(Thread):
    def __init__(self):
        super().__init__(name="Shell", daemon=True)
        self.io_loop = IOLoop(make_current=False)

    def run(self):
        self.io_loop.make_current()
        try:
            self.io_loop.start()
        finally:
            self.io_loop.close()
