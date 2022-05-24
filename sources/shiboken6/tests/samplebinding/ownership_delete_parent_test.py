#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for destroying the parent'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType


class DeleteParentTest(unittest.TestCase):
    '''Test case for deleting a parent object'''

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testParentDestructor(self):
        '''Delete parent object should invalidate child'''
        parent = ObjectType()
        child = ObjectType()
        child.setParent(parent)

        refcount_before = sys.getrefcount(child)

        del parent
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertRaises(RuntimeError, child.objectName)
        self.assertEqual(sys.getrefcount(child), refcount_before-1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testParentDestructorMultipleChildren(self):
        '''Delete parent object should invalidate all children'''
        parent = ObjectType()
        children = [ObjectType() for _ in range(10)]

        for child in children:
            child.setParent(parent)

        del parent
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        for i, child in enumerate(children):
            self.assertRaises(RuntimeError, child.objectName)
            self.assertEqual(sys.getrefcount(child), 4)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRecursiveParentDelete(self):
        '''Delete parent should invalidate grandchildren'''
        parent = ObjectType()
        child = ObjectType(parent)
        grandchild = ObjectType(child)

        del parent
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertRaises(RuntimeError, child.objectName)
        self.assertEqual(sys.getrefcount(child), 2)
        self.assertRaises(RuntimeError, grandchild.objectName)
        self.assertEqual(sys.getrefcount(grandchild), 2)


if __name__ == '__main__':
    unittest.main()
