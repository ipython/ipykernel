"""Utilities to manipulate JSON objects."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import re
from datetime import datetime

from jupyter_client._version import version_info as jupyter_client_version

next_attr_name = "__next__"

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------

# timestamp formats
ISO8601 = "%Y-%m-%dT%H:%M:%S.%f"
ISO8601_PAT = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d{1,6})?Z?([\+\-]\d{2}:?\d{2})?$"
)

# holy crap, strptime is not threadsafe.
# Calling it once at import seems to help.
datetime.strptime("2000-01-01", "%Y-%m-%d")

# -----------------------------------------------------------------------------
# Classes and functions
# -----------------------------------------------------------------------------


# constants for identifying png/jpeg data
PNG = b"\x89PNG\r\n\x1a\n"
# front of PNG base64-encoded
PNG64 = b"iVBORw0KG"
JPEG = b"\xff\xd8"
# front of JPEG base64-encoded
JPEG64 = b"/9"
# constants for identifying gif data
GIF_64 = b"R0lGODdh"
GIF89_64 = b"R0lGODlh"
# front of PDF base64-encoded
PDF64 = b"JVBER"

JUPYTER_CLIENT_MAJOR_VERSION = jupyter_client_version[0]


def encode_images(format_dict):
    """b64-encodes images in a displaypub format dict

    Parameters
    ----------
    format_dict : dict
        A dictionary of display data keyed by mime-type

    Returns
    -------
    format_dict : dict
        A copy of the same dictionary,
        but binary image data ('image/png', 'image/jpeg' or 'application/pdf')
        is base64-encoded.

    """

    # no need for handling of ambiguous bytestrings on Python 3,
    # where bytes objects always represent binary data and thus
    # base64-encoded.
    return format_dict
