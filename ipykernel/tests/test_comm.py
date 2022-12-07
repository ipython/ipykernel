from ipykernel.comm import Comm
from ipykernel.ipkernel import IPythonKernel



async def test_comm(kernel):
    c = Comm()
    c.kernel = kernel  # type:ignore
    c.publish_msg("foo")


def test_comm_in_manager(ipkernel: IPythonKernel) -> None:
    comm = Comm()
    assert comm.comm_id in ipkernel.comm_manager.comms
