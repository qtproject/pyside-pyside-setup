#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import OnlyCopy, FriendOfOnlyCopy

class ClassWithOnlyCopyCtorTest(unittest.TestCase):
    def testGetOne(self):
        obj = FriendOfOnlyCopy.createOnlyCopy(123)
        self.assertEqual(type(obj), OnlyCopy)
        self.assertEqual(obj.value(), 123)

    def testGetMany(self):
        objs = FriendOfOnlyCopy.createListOfOnlyCopy(3)
        self.assertEqual(type(objs), list)
        self.assertEqual(len(objs), 3)
        for value, obj in enumerate(objs):
            self.assertEqual(obj.value(), value)

    def testPassAsValue(self):
        obj = FriendOfOnlyCopy.createOnlyCopy(123)
        self.assertEqual(obj.value(), OnlyCopy.getValue(obj))

    def testPassAsReference(self):
        obj = FriendOfOnlyCopy.createOnlyCopy(123)
        self.assertEqual(obj.value(), OnlyCopy.getValueFromReference(obj))

if __name__ == '__main__':
    unittest.main()
