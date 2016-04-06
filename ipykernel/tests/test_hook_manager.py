# -*- coding: utf-8 -*-
""" Tests for zmq shell / display publisher. """

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import unittest
from traitlets import Int
import zmq

from ipykernel.zmqshell import ZMQDisplayPublisher
from ipykernel.hookmanager import MessageHookFor
from jupyter_client.session import Session

from .utils import new_kernel


class HookManagerTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_blah(self):
        with new_kernel() as kc:
            with MessageHookFor('display_data'):
                print('Hooked')


if __name__ == '__main__':
    unittest.main()
