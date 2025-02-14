"""An in-process terminal example."""

import os

from anyio import run
from jupyter_console.ptshell import ZMQTerminalInteractiveShell

from ipykernel.inprocess.manager import InProcessKernelManager


def print_process_id():
    """Print the process id."""
    print("Process ID is:", os.getpid())


async def main():
    """The main function."""
    print_process_id()

    # Create an in-process kernel
    # >>> print_process_id()
    # will print the same process ID as the main process
    kernel_manager = InProcessKernelManager()
    await kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = "qt4"
    kernel.shell.push({"foo": 43, "print_process_id": print_process_id})
    client = kernel_manager.client()
    client.start_channels()

    shell = ZMQTerminalInteractiveShell(manager=kernel_manager, client=client)
    shell.mainloop()


if __name__ == "__main__":
    run(main)
