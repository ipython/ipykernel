"""Test suite for our JSON utilities."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from ipykernel.jsonutil import encode_images, json_clean


def test_json_clean_is_noop():
    for obj in (1, "a", [1, 2], {"x": (1, 2)}, object()):
        assert json_clean(obj) is obj


def test_encode_images_is_noop():
    fmt = {"image/png": b"\x89PNG\r\n\x1a\n", "text/plain": "hi"}
    assert encode_images(fmt) is fmt
