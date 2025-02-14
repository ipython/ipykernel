"""An in-process qt console app."""

import os

import tornado
from IPython.lib import guisupport
from qtconsole.inprocess import QtInProcessKernelManager
from qtconsole.rich_ipython_widget import RichIPythonWidget

assert tornado.version_info >= (6, 1)


def print_process_id():
    """Print the process id."""
    print("Process ID is:", os.getpid())


def main():
    """The main entry point."""
    # Print the ID of the main process
    print_process_id()

    app = guisupport.get_app_qt4()

    # Create an in-process kernel
    # >>> print_process_id()
    # will print the same process ID as the main process
    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = "qt4"
    kernel.shell.push({"foo": 43, "print_process_id": print_process_id})

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()
        app.exit()

    control = RichIPythonWidget()
    control.kernel_manager = kernel_manager
    control.kernel_client = kernel_client
    control.exit_requested.connect(stop)
    control.show()

    guisupport.start_event_loop_qt4(app)


if __name__ == "__main__":
    main()
