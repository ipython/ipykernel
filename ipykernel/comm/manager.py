"""Base class to manage comms"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.


import comm.base_comm
import traitlets.config


class CommManager(traitlets.config.LoggingConfigurable, comm.base_comm.CommManager):
    def __init__(self, **kwargs):
        # CommManager doesn't take arguments, so we explicitly forward arguments
        traitlets.config.LoggingConfigurable.__init__(self, **kwargs)
        comm.base_comm.CommManager.__init__(self)
