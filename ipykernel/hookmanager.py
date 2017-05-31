# -*- coding: utf-8 -*-
"""
A context manager that will register a hook on a
Display Publisher for storing messages.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from io import StringIO
import sys

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
    def __init__(self, message_name, parent=None):
        self._parent = parent
        self._message_name = message_name
        self._pub = get_ipython().display_pub
        self._hook = ZMQMessageHook(message_name, parent.store)
        self._callback = parent.store
        self._std_buffer = StringIO()

    def clear_output(self, *args, **kwargs):
        self._std_buffer.truncate(0)
        self._parent.clear()

    def __enter__(self):
        """
        Called on entry to the context.

        Installs the message hook on the current ipython
        display publisher.
        """
        self._pub.register_hook(self._hook)
        self._old_clear = self._pub.clear_output
        self._pub.clear_output = self.clear_output

        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        sys.stdout = self._std_buffer
        sys.stderr = self._std_buffer

    def __exit__(self, tp, value, tb):
        if tp is not None:
            # Exception occurred... log and continue.
            pass

        self._pub.unregister_hook(self._hook)
        self._pub.clear_output = self._old_clear
        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr

        std = self._std_buffer.getvalue()
        if std:
            # TODO : update this once rendermime is available here.
            temp = {'content': {'data': {'text/plain': std}}}
            self._callback(temp)
            self._std_buffer.truncate(0)

        return False
