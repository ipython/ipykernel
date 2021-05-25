"""Configurable for configuring the IPython inline backend

This module does not import anything from matplotlib.
"""

import warnings

from matplotlib_inline.config import * # analysis: ignore


warnings.warn(
    "`ipykernel.pylab.config` is deprecated, directly "
    "use `matplotlib_inline.config`",
    DeprecationWarning
)
