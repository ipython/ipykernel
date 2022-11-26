"""Base class for a Comm"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from typing import Optional

import comm.base_comm
import traitlets.config

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
class Comm(traitlets.config.LoggingConfigurable, BaseComm):
    """Class for communicating between a Frontend and a Kernel"""

    def __init__(self, *args, **kwargs):
        self.kernel = None
        # Comm takes positional arguments, LoggingConfigurable does not, so we explicitly forward arguments
        traitlets.config.LoggingConfigurable.__init__(self, **kwargs)
        BaseComm.__init__(self, *args, **kwargs)


__all__ = ["Comm"]
