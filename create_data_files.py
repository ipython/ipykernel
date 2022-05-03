import os
import sys
import shutil

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

from ipykernel.kernelspec import KERNEL_NAME, make_ipkernel_cmd, write_kernel_spec


# When building a dist, the executable specified in the kernelspec is simply 'python'.
if "--dist" in sys.argv:
    argv = make_ipkernel_cmd(executable="python")

 # When installing from source, the full `sys.executable` can be used.
else:
    argv = make_ipkernel_cmd()



dest = os.path.join(here, "jupyter-data", "share", "jupyter", "kernels", KERNEL_NAME)
if os.path.exists(dest):
    shutil.rmtree(dest)

os.makedirs(dest)
write_kernel_spec(dest, overrides={"argv": argv})
