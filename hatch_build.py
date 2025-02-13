"""A custom hatch build hook for ipykernel."""

import shutil
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomHook(BuildHookInterface):
    """The IPykernel build hook."""

    def initialize(self, version, build_data):
        """Initialize the hook."""
        here = Path(__file__).parent.resolve()
        sys.path.insert(0, str(here))
        from ipykernel.kernelspec import make_ipkernel_cmd, write_kernel_spec

        overrides = {}

        # When building a standard wheel, the executable specified in the kernelspec is simply 'python'.
        if version == "standard":
            overrides["metadata"] = dict(debugger=True)
            argv = make_ipkernel_cmd(executable="python")

        # When installing an editable wheel, the full `sys.executable` can be used.
        else:
            argv = make_ipkernel_cmd()

        overrides["argv"] = argv

        dest = Path(here) / "data_kernelspec"
        if Path(dest).exists():
            shutil.rmtree(dest)

        write_kernel_spec(dest, overrides=overrides)
