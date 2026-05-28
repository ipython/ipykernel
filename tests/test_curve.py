# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import time

import pytest
import zmq
from jupyter_client import KernelManager

from ipykernel.kernelapp import IPKernelApp


@pytest.fixture
def curve_disabled_kernel_app(tmp_path):
    app, connection_file_path = _make_app(tmp_path, enable_curve=False)
    try:
        yield app, connection_file_path
    finally:
        app.close()


@pytest.fixture
def curve_enabled_kernel_app(tmp_path):
    app, connection_file_path = _make_app(tmp_path, enable_curve=True)
    try:
        yield app, connection_file_path
    finally:
        app.close()


def test_connection_file_no_curve_keys_by_default(curve_disabled_kernel_app):
    """Connection file must not contain curve keys when Curve is disabled."""
    app, connection_file_path = curve_disabled_kernel_app
    app.init_sockets()
    app.init_heartbeat()
    app.write_connection_file()
    with open(connection_file_path) as f:
        info = json.load(f)
    assert "curve_publickey" not in info
    assert "curve_secretkey" not in info


def test_curve_connection_file_has_keys(curve_enabled_kernel_app):
    """When Curve is enabled the connection file must carry both keys."""
    app, connection_file_path = curve_enabled_kernel_app
    app.init_sockets()
    app.init_heartbeat()
    app.write_connection_file()
    with open(connection_file_path) as f:
        info = json.load(f)
    assert "curve_publickey" in info, "curve_publickey missing from connection file"
    assert "curve_secretkey" in info, "curve_secretkey missing from connection file"
    # Keys are Z85-encoded ASCII strings - always exactly 40 characters.
    assert len(info["curve_publickey"]) == 40
    assert len(info["curve_secretkey"]) == 40
    # Existing fields must still be present (backward-compat check).
    assert "key" in info
    assert "shell_port" in info


def test_curve_keys_are_stable_per_startup(curve_enabled_kernel_app):
    """Provisioned keys stay unchanged throughout the kernel process lifetime."""
    app, _connection_file_path = curve_enabled_kernel_app
    app.init_sockets()
    pub1 = app.curve_publickey
    # Writing the file twice should not regenerate keys.
    app.init_heartbeat()
    app.write_connection_file()
    assert app.curve_publickey == pub1


def test_curve_socket_server_options(curve_enabled_kernel_app):
    """Bound sockets must have CURVE_SERVER=True when Curve is enabled."""
    app, _connection_file_path = curve_enabled_kernel_app
    app.init_sockets()
    # shell and stdin are ROUTER sockets configured directly.
    assert app.shell_socket.curve_server, "shell_socket missing curve_server"
    assert app.stdin_socket.curve_server, "stdin_socket missing curve_server"
    assert app.control_socket.curve_server, "control_socket missing curve_server"
    # Key material is write-only in pyzmq; we verify it was applied
    # through the curve_server flag and the reject test below.


def test_no_curve_socket_options_when_disabled(curve_disabled_kernel_app):
    """No CURVE options are set when Curve is disabled (default)."""
    app, _connection_file_path = curve_disabled_kernel_app
    app.init_sockets()
    # curve_server defaults to 0/False; key options are write-only.
    assert not app.shell_socket.curve_server


def test_curve_unauthenticated_socket_messages_dropped(curve_enabled_kernel_app):
    """With CurveZMQ, frames from a socket without the server key are dropped.

    This is the core security property: a raw DEALER socket that connects to
    a CURVE_SERVER-enabled ROUTER cannot deliver messages to it.  Compare
    with test_transport_security.py in jupyter-client which shows the *absence*
    of this property today.
    """
    app, _connection_file_path = curve_enabled_kernel_app
    app.init_sockets()

    # Build the endpoint URL from the bound port.
    endpoint = f"tcp://{app.ip}:{app.shell_port}"

    ctx = zmq.Context()
    unauth = ctx.socket(zmq.DEALER)
    try:
        unauth.connect(endpoint)
        # ZMQ delivers the connect synchronously, but the curve
        # handshake silently drops the message.
        unauth.send(b"probe", flags=zmq.NOBLOCK)

        poller = zmq.Poller()
        poller.register(app.shell_socket, zmq.POLLIN)
        events = dict(poller.poll(timeout=300))
        assert app.shell_socket not in events, (
            "Unauthenticated message reached the kernel socket - CurveZMQ should have dropped it"
        )
    finally:
        unauth.close(linger=0)
        ctx.term()


def test_curve_authenticated_socket_can_communicate(curve_enabled_kernel_app):
    """With CurveZMQ, a correctly-keyed client socket can reach the kernel."""
    app, _connection_file_path = curve_enabled_kernel_app
    app.init_sockets()

    endpoint = f"tcp://{app.ip}:{app.shell_port}"
    server_public = app.curve_publickey

    ctx = zmq.Context()
    auth_client = ctx.socket(zmq.DEALER)
    # Client uses the server's public key as CURVE_SERVERKEY; its own
    # keypair is used only for encryption, not for access control.
    client_pub, client_sec = zmq.curve_keypair()
    auth_client.curve_secretkey = client_sec
    auth_client.curve_publickey = client_pub
    auth_client.curve_serverkey = server_public
    try:
        auth_client.connect(endpoint)
        # Allow the handshake to complete.
        time.sleep(0.05)
        auth_client.send(b"probe", flags=zmq.NOBLOCK)

        poller = zmq.Poller()
        poller.register(app.shell_socket, zmq.POLLIN)
        events = dict(poller.poll(timeout=1000))
        assert app.shell_socket in events, (
            "Authenticated client message was not received by kernel socket"
        )
    finally:
        auth_client.close(linger=0)
        ctx.term()


def test_manager_provisioned_curve_keys_are_used(curve_enabled_kernel_app):
    """Kernel uses manager-provisioned Curve keys exactly as provided."""
    app, _connection_file_path = curve_enabled_kernel_app
    try:
        with open(_connection_file_path) as f:
            info = json.load(f)

        app.init_sockets()

        assert app.curve_publickey == info["curve_publickey"].encode()
        assert app.curve_secretkey == info["curve_secretkey"].encode()
        assert app.shell_socket.curve_server
        assert app.stdin_socket.curve_server
        assert app.control_socket.curve_server
    finally:
        app.close()


def _make_app(tmp_path, *, enable_curve=False, **kwargs):
    """Return a minimal IPKernelApp rooted in temporary directory *tmp_path*."""
    connection_file_path = str(tmp_path / "kernel.json")
    if enable_curve:
        # Populate the Curve keys into the connection file
        km = KernelManager(connection_file=connection_file_path)
        km.transport_encryption = "enabled"
        km.pre_start_kernel()

    app = IPKernelApp(connection_file=connection_file_path, **kwargs)
    # Replicate the subset of initialize() that sets up connection info
    # without importing IPython shell machinery.
    super(IPKernelApp, app).initialize(argv=[""])
    app.init_connection_file()
    return app, connection_file_path
