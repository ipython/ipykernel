"""Base class for a Comm"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import uuid
from typing import Optional

import comm.base_comm
import traitlets.config
from traitlets import Bool, Bytes, Instance, Unicode, default

from ipykernel.jsonutil import json_clean
from ipykernel.kernelbase import Kernel


# this is the class that will be created if we do comm.create_comm
class BaseComm(comm.base_comm.BaseComm):
    kernel: Optional[Kernel] = None

    def publish_msg(self, msg_type, data=None, metadata=None, buffers=None, **keys):
        """Helper for sending a comm message on IOPub"""
        if not Kernel.initialized():
            return

        data = {} if data is None else data
        metadata = {} if metadata is None else metadata
        content = json_clean(dict(data=data, comm_id=self.comm_id, **keys))

        if self.kernel is None:
            self.kernel = Kernel.instance()

        self.kernel.session.send(
            self.kernel.iopub_socket,
            msg_type,
            content,
            metadata=json_clean(metadata),
            parent=self.kernel.get_parent("shell"),
            ident=self.topic,
            buffers=buffers,
        )


# but for backwards compatibility, we need to inherit from LoggingConfigurable
class Comm(traitlets.config.LoggingConfigurable):
    """Class for communicating between a Frontend and a Kernel"""

    kernel = Instance("ipykernel.kernelbase.Kernel", allow_none=True)
    comm_id = Unicode()
    primary = Bool(True, help="Am I the primary or secondary Comm?")

    target_name = Unicode("")
    target_module = Unicode(
        None,
        allow_none=True,
        help="""requirejs module from
        which to load comm target.""",
    )

    topic = Bytes()

    @default("kernel")
    def _default_kernel(self):
        if Kernel.initialized():
            return Kernel.instance()

    @default("comm_id")
    def _default_comm_id(self):
        return uuid.uuid4().hex

    def __init__(self, target_name='', data=None, metadata=None, buffers=None, **kwargs):
        if target_name:
            kwargs['target_name'] = target_name
        super().__init__(**kwargs)
        self._comm = BaseComm(data=data, metadata=metadata, buffers=buffers, **kwargs)

    def open(self, data=None, metadata=None, buffers=None):
        """Open the frontend-side version of this comm"""
        self._comm.open(data=data, metadata=metadata, buffers=buffers)

    def close(self, data=None, metadata=None, buffers=None, deleting=False):
        """Close the frontend-side version of this comm"""
        self._comm.close(data=data, metadata=metadata, buffers=buffers, deleting=deleting)

    def send(self, data=None, metadata=None, buffers=None):
        """Send a message to the frontend-side version of this comm"""
        self._comm.publish_msg("comm_msg", data=data, metadata=metadata, buffers=buffers)

    # registering callbacks

    def on_close(self, callback):
        """Register a callback for comm_close

        Will be called with the `data` of the close message.

        Call `on_close(None)` to disable an existing callback.
        """
        self._comm.on_close(callback)

    def on_msg(self, callback):
        """Register a callback for comm_msg

        Will be called with the `data` of any comm_msg messages.

        Call `on_msg(None)` to disable an existing callback.
        """
        self._comm.on_msg(callback)

    # handling of incoming messages

    def handle_close(self, msg):
        """Handle a comm_close message"""
        self._comm.handle_close(msg)

    def handle_msg(self, msg):
        """Handle a comm_msg message"""
        self._comm.handle_close(msg)


__all__ = ["Comm"]
