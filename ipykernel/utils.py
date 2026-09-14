"""Utilities"""

from __future__ import annotations

import asyncio
import typing as t
from collections.abc import Mapping
from contextvars import copy_context
from functools import wraps

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from contextvars import Context


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


T = t.TypeVar("T")
U = t.TypeVar("U")
V = t.TypeVar("V")


def _async_in_context(
    f: Callable[..., t.Coroutine[T, U, V]], context: Context | None = None
) -> Callable[..., t.Coroutine[T, U, V]]:
    """
    Wrapper to run a coroutine in a persistent ContextVar Context.
    """
    if context is None:
        context = copy_context()

    @wraps(f)
    async def run_in_context(*args, **kwargs):
        coro = f(*args, **kwargs)
        return await asyncio.create_task(coro, context=context)

    return run_in_context
