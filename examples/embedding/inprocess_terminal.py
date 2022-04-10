import os
import sys

import tornado
from jupyter_console.ptshell import ZMQTerminalInteractiveShell

from ipykernel.inprocess.manager import InProcessKernelManager


def print_process_id():
    print("Process ID is:", os.getpid())


def init_asyncio_patch():
    """set default asyncio policy to be compatible with tornado
    Tornado 6 (at least) is not compatible with the default
    asyncio implementation on Windows
    Pick the older SelectorEventLoopPolicy on Windows
    if the known-incompatible default policy is in use.
    do this as early as possible to make it a low priority and overrideable
    ref: https://github.com/tornadoweb/tornado/issues/2608
    FIXME: if/when tornado supports the defaults in asyncio,
           remove and bump tornado requirement for py38
    """
    if (
        sys.platform.startswith("win")
        and sys.version_info >= (3, 8)
        and tornado.version_info < (6, 1)
    ):
        import asyncio

        try:
            from asyncio import (
                WindowsProactorEventLoopPolicy,
                WindowsSelectorEventLoopPolicy,
            )
        except ImportError:
            pass
            # not affected
        else:
            if type(asyncio.get_event_loop_policy()) is WindowsProactorEventLoopPolicy:
                # WindowsProactorEventLoopPolicy is not compatible with tornado 6
                # fallback to the pre-3.8 default of Selector
                asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def main():
    print_process_id()

    # Create an in-process kernel
    # >>> print_process_id()
    # will print the same process ID as the main process
    init_asyncio_patch()
    kernel_manager = InProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = "qt4"
    kernel.shell.push({"foo": 43, "print_process_id": print_process_id})
    client = kernel_manager.client()
    client.start_channels()

    shell = ZMQTerminalInteractiveShell(manager=kernel_manager, client=client)
    shell.mainloop()


if __name__ == "__main__":
    main()
