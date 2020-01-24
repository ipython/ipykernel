import builtins
import logging
import traceback

import trio


class TrioRunner:
    def __init__(self):
        self._trio_token = None

    def run(self):
        def log_nursery_exc(exc):
            exc = '\n'.join(traceback.format_exception(type(exc), exc,
                exc.__traceback__))
            logging.error('An exception occurred in a global nursery task.\n%s',
                exc)

        async def trio_main():
            self._trio_token = trio.hazmat.current_trio_token()
            async with trio.open_nursery() as nursery:
                # TODO This hack prevents the nursery from cancelling all child
                # tasks when an uncaught exception occurs, but it's ugly.
                nursery._add_exc = log_nursery_exc
                builtins.GLOBAL_NURSERY = nursery
                await trio.sleep_forever()

        trio.run(trio_main)

    def __call__(self, async_fn):
        async def loc(coro):
            """
            We need the dummy no-op async def to protect from
            trio's internal. See https://github.com/python-trio/trio/issues/89
            """
            return await coro

        return trio.from_thread.run(loc, async_fn, trio_token=self._trio_token)
