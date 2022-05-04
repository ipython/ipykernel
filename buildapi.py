"""A build backend that handles installing the ipykernel kernelspec.

See https://peps.python.org/pep-0517/#in-tree-build-backends
"""
import os
import shutil
import sys

from flit_core.buildapi import build_editable  # noqa
from flit_core.buildapi import build_sdist  # noqa
from flit_core.buildapi import build_wheel  # noqa
from flit_core.buildapi import (
    get_requires_for_build_editable as get_requires_for_build_editable_orig,
)
from flit_core.buildapi import (
    get_requires_for_build_sdist as get_requires_for_build_sdist_orig,
)
from flit_core.buildapi import (
    get_requires_for_build_wheel as get_requires_for_build_wheel_orig,
)

from ipykernel.kernelspec import KERNEL_NAME, make_ipkernel_cmd, write_kernel_spec


def make_kernel_spec(executable=None):
    argv = make_ipkernel_cmd(executable=executable)

    here = os.path.abspath(os.path.dirname(__file__))
    dest = os.path.join(here, "jupyter-data", "share", "jupyter", "kernels", KERNEL_NAME)
    if os.path.exists(dest):
        shutil.rmtree(dest)

    write_kernel_spec(dest, overrides={"argv": argv})


def get_requires_for_build_wheel(config_settings=None):
    make_kernel_spec(executable="python")
    return get_requires_for_build_wheel_orig(config_settings=config_settings)


def get_requires_for_build_sdist(config_settings=None):
    make_kernel_spec(executable="python")
    return get_requires_for_build_sdist_orig(config_settings=config_settings)


def get_requires_for_build_editable(config_settings=None):
    make_kernel_spec(executable=sys.executable)
    return get_requires_for_build_editable_orig(config_settings=config_settings)
