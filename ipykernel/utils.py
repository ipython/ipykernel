from __future__ import annotations

from typing import Any

import zmq


def create_inproc_pair_socket(
    context: zmq.Context[Any], name: str | None, shell_channel_end: bool
) -> zmq.Socket[Any]:
    """Create and return a single ZMQ inproc pair socket."""
    address = get_inproc_socket_address(name)
    socket: zmq.Socket[Any] = context.socket(zmq.PAIR)
    if shell_channel_end:
        socket.bind(address)
    else:
        socket.connect(address)
    return socket


def get_inproc_socket_address(name: str | None) -> str:
    full_name = f"subshell-{name}" if name else "subshell"
    return f"inproc://{full_name}"
