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

from sample import Point

class ExtPoint(Point): pass

class TestWritableClassDict(unittest.TestCase):
    def testSetattrOnClass(self):
        setattr(Point, 'foo', 123)
        self.assertEqual(Point.foo, 123)
        pt = Point()
        self.assertEqual(pt.foo, 123)

    def testSetattrOnInheritingClass(self):
        setattr(Point, 'bar', 321)
        self.assertEqual(Point.bar, 321)
        self.assertEqual(ExtPoint.bar, 321)
        pt = ExtPoint()
        self.assertEqual(pt.bar, 321)

if __name__ == '__main__':
    unittest.main()
