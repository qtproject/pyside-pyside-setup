#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Simple event loop dispatcher test.'''

import os
import sys
import time
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from random import random

from sample import ObjectType, Event


class NoOverride(ObjectType):

    pass


class Override(ObjectType):

    def __init__(self):
        ObjectType.__init__(self)
        self.called = False

    def event(self, event):
        self.called = True
        return True


class TestEventLoop(unittest.TestCase):

    def testEventLoop(self):
        '''Calling virtuals in a event loop'''
        objs = [ObjectType(), NoOverride(), Override()]

        evaluated = ObjectType.processEvent(objs,
                                        Event(Event.BASIC_EVENT))

        self.assertEqual(evaluated, 3)
        self.assertTrue(objs[2].called)


if __name__ == '__main__':
    unittest.main()
