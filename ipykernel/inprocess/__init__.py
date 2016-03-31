# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from .channels import (
    InProcessChannel,
    InProcessHBChannel,
)

from .client import InProcessKernelClient
from .manager import InProcessKernelManager
from .blocking import BlockingInProcessKernelClient
