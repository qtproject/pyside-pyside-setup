#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for virtual methods in multiple inheritance scenarios'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import VirtualMethods, ObjectType, Event


class ImplementsNone(ObjectType, VirtualMethods):
    '''Implements no virtual methods'''

    def __init__(self):
        ObjectType.__init__(self)
        VirtualMethods.__init__(self)


class ImplementsBoth(ObjectType, VirtualMethods):
    '''Implements ObjectType.event and VirtualMethods.sum1'''

    def __init__(self):
        ObjectType.__init__(self)
        VirtualMethods.__init__(self)
        self.event_processed = False

    def event(self, event):
        self.event_processed = True
        return True

    def sum1(self, arg0, arg1, arg2):
        return (arg0 + arg1 + arg2) * 2


class CppVirtualTest(unittest.TestCase):
    '''Virtual method defined in c++ called from C++'''

    def testCpp(self):
        '''C++ calling C++ virtual method in multiple inheritance scenario'''
        obj = ImplementsNone()
        self.assertTrue(ObjectType.processEvent([obj], Event(Event.BASIC_EVENT)))
        self.assertRaises(AttributeError, getattr, obj, 'event_processed')

        self.assertEqual(obj.callSum0(1, 2, 3), 6)


class PyVirtualTest(unittest.TestCase):
    '''Virtual method reimplemented in python called from C++'''

    def testEvent(self):
        '''C++ calling Python reimplementation of virtual in multiple inheritance'''
        obj = ImplementsBoth()
        self.assertTrue(ObjectType.processEvent([obj], Event(Event.BASIC_EVENT)))
        self.assertTrue(obj.event_processed)

        self.assertEqual(obj.callSum1(1, 2, 3), 12)


if __name__ == '__main__':
    unittest.main()
