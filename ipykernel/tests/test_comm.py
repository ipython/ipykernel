from ipykernel.comm import Comm


async def test_comm(kernel):
    c = Comm()
    c.kernel = kernel  # type:ignore
    c.publish_msg("foo")
