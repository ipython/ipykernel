"""Utilities"""

import typing as t
from collections.abc import Mapping


class LazyDict(Mapping[str, t.Any]):
    """Lazy evaluated read-only dictionary.

    Initialised with a dictionary of key-value pairs where the values are either
    constants or callables. Callables are evaluated each time the respective item is
    read.
    """

    def __init__(self, dict):
        self._dict = dict

    def __getitem__(self, key):
        item = self._dict.get(key)
        return item() if callable(item) else item

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)
