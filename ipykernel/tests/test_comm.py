from ipykernel.comm import Comm


async def test_comm(kernel):
    c = Comm()
    c.kernel = kernel
    c.publish_msg("foo")
