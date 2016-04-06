# -*- coding: utf-8 -*-
"""
A context manager that will register a hook on a
Display Publisher for storing messages.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from IPython.core.getipython import get_ipython

from .displayhook import ZMQMessageHook


class MessageHookFor(object):
    """
    A context manager which takes the name of a message field,
    and installs a hook to intercept messages of that type.

    Usage
    -----
    >>> with MessageHookFor('display_data'):
            clear_output()
    """
    def __init__(self, message_name):
        self._message_name = message_name
        self._pub = get_ipython().display_pub
        self._hook = ZMQMessageHook(message_name)

    def __enter__(self):
        """
        Called on entry to the context.

        Installs the message hook on the current ipython
        display publisher.
        """
        self._pub.register_hook(self._hook)

    def __exit__(self, tp, value, tb):
        if tp is not None:
            # Exception occurred... log and continue.
            pass

        self._pub.unregister_hook(self._hook)
