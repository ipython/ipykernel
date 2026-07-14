"""Utilities to manipulate JSON objects."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.


def encode_images(format_dict):
    """Deprecated: this is a no-op.

    b64-encoding of image data is handled upstream, where bytes objects
    always represent binary data.

    Parameters
    ----------
    format_dict : dict
        A dictionary of display data keyed by mime-type

    Returns
    -------
    format_dict : dict
        The unmodified input dictionary.
    """
    return format_dict


def json_clean(obj):
    """Deprecated: this is a no-op.

    JSON sanitization is handled by jupyter-client (>=7) at serialization
    time, so objects are returned unmodified.

    Parameters
    ----------
    obj : any python object

    Returns
    -------
    out : object
        The unmodified input object.
    """
    return obj
