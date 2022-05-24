#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for invalidating a parent of other objects.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType, BlackBox


class InvalidateParentTest(unittest.TestCase):
    '''Tests for invalidating a parent of other objects.'''

    def testInvalidateParent(self):
        '''Invalidate parent should invalidate children'''
        parent = ObjectType.create()
        child1 = ObjectType(parent)
        child1.setObjectName("child1")
        child2 = ObjectType.create()
        child2.setObjectName("child2")
        child2.setParent(parent)
        grandchild1 = ObjectType(child1)
        grandchild1.setObjectName("grandchild1")
        grandchild2 = ObjectType.create()
        grandchild2.setObjectName("grandchild2")
        grandchild2.setParent(child2)
        bbox = BlackBox()

        bbox.keepObjectType(parent) # Should invalidate the parent

        self.assertRaises(RuntimeError, parent.objectName)
        # some children still valid they are wrapper classes
        self.assertEqual(child1.objectName(), "child1")
        self.assertRaises(RuntimeError, child2.objectName)
        self.assertEqual(grandchild1.objectName(), "grandchild1")
        self.assertRaises(RuntimeError, grandchild2.objectName)

if __name__ == '__main__':
    unittest.main()

