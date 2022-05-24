#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''The BlackBox class has cases of ownership transference between C++ and Python.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType, BlackBox

class BlackBoxTest(unittest.TestCase):
    '''The BlackBox class has cases of ownership transference between C++ and Python.'''

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testOwnershipTransference(self):
        '''Ownership transference from Python to C++ and back again.'''
        o1 = ObjectType()
        o1.setObjectName('object1')
        o1_refcnt = sys.getrefcount(o1)
        o2 = ObjectType()
        o2.setObjectName('object2')
        o2_refcnt = sys.getrefcount(o2)
        bb = BlackBox()
        o1_ticket = bb.keepObjectType(o1)
        o2_ticket = bb.keepObjectType(o2)
        self.assertEqual(set(bb.objects()), set([o1, o2]))
        self.assertEqual(str(o1.objectName()), 'object1')
        self.assertEqual(str(o2.objectName()), 'object2')
        self.assertEqual(sys.getrefcount(o1), o1_refcnt + 1) # PySide give +1 ref to object with c++ ownership
        self.assertEqual(sys.getrefcount(o2), o2_refcnt + 1)
        o2 = bb.retrieveObjectType(o2_ticket)
        self.assertEqual(sys.getrefcount(o2), o2_refcnt)
        del bb
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertRaises(RuntimeError, o1.objectName)
        self.assertEqual(str(o2.objectName()), 'object2')
        self.assertEqual(sys.getrefcount(o2), o2_refcnt)

    def testBlackBoxReleasingUnknownObjectType(self):
        '''Asks BlackBox to release an unknown ObjectType.'''
        o1 = ObjectType()
        o2 = ObjectType()
        bb = BlackBox()
        o1_ticket = bb.keepObjectType(o1)
        o3 = bb.retrieveObjectType(-5)
        self.assertEqual(o3, None)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testOwnershipTransferenceCppCreated(self):
        '''Ownership transference using a C++ created object.'''
        o1 = ObjectType.create()
        o1.setObjectName('object1')
        o1_refcnt = sys.getrefcount(o1)
        bb = BlackBox()
        o1_ticket = bb.keepObjectType(o1)
        self.assertRaises(RuntimeError, o1.objectName)

if __name__ == '__main__':
    unittest.main()

