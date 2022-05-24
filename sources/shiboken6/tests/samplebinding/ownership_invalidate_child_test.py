#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for invalidating a C++ created child that was already on the care of a parent.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType, BlackBox


class InvalidateChildTest(unittest.TestCase):
    '''Tests for invalidating a C++ created child that was already on the care of a parent.'''

    def testInvalidateChild(self):
        '''Invalidating method call should remove child from the care of a parent if it has one.'''
        parent = ObjectType()
        child1 = ObjectType(parent)
        child1.setObjectName('child1')
        child2 = ObjectType.create()
        child2.setParent(parent)
        child2.setObjectName('child2')

        self.assertEqual(parent.children(), [child1, child2])

        bbox = BlackBox()

        # This method steals ownership from Python to C++.
        bbox.keepObjectType(child1)
        self.assertEqual(parent.children(), [child2])

        bbox.keepObjectType(child2)
        self.assertEqual(parent.children(), [])

        del parent
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()

        self.assertEqual(child1.objectName(), 'child1')
        self.assertRaises(RuntimeError, child2.objectName)

if __name__ == '__main__':
    unittest.main()

