import os
import shutil
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):

        here = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, here)
        from ipykernel.kernelspec import make_ipkernel_cmd, write_kernel_spec

        # When building a standard wheel, the executable specified in the kernelspec is simply 'python'.
        if version == "standard":
            argv = make_ipkernel_cmd(executable="python")

        # When installing an editable wheel, the full `sys.executable` can be used.
        else:
            argv = make_ipkernel_cmd()

        dest = os.path.join(here, "data_kernelspec")
        if os.path.exists(dest):
            shutil.rmtree(dest)
        write_kernel_spec(dest, overrides={"argv": argv})
