#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for multiple inheritance'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *

class SimpleUseCase(ObjectType, Str):
    def __init__(self, name):
        ObjectType.__init__(self)
        Str.__init__(self, name)

class SimpleUseCaseReverse(Str, ObjectType):
    def __init__(self, name):
        ObjectType.__init__(self)
        Str.__init__(self, name)

class SimpleUseCase2(SimpleUseCase):
    def __init__(self, name):
        SimpleUseCase.__init__(self, name)

class ComplexUseCase(SimpleUseCase2, Point):
    def __init__(self, name):
        SimpleUseCase2.__init__(self, name)
        Point.__init__(self)

class ComplexUseCaseReverse(Point, SimpleUseCase2):
    def __init__(self, name):
        SimpleUseCase2.__init__(self, name)
        Point.__init__(self)

class MultipleCppDerivedTest(unittest.TestCase):
    def testInstanciation(self):
        s = SimpleUseCase("Hi")
        self.assertEqual(s, "Hi")
        s.setObjectName(s)
        self.assertEqual(s.objectName(), "Hi")

    def testInstanciation2(self):
        s = SimpleUseCase2("Hi")
        self.assertEqual(s, "Hi")
        s.setObjectName(s)
        self.assertEqual(s.objectName(), "Hi")

    def testComplexInstanciation(self):
        c = ComplexUseCase("Hi")
        self.assertEqual(c, "Hi")
        c.setObjectName(c)
        self.assertEqual(c.objectName(), "Hi")
        c.setX(2);
        self.assertEqual(c.x(), 2)

class MultipleCppDerivedReverseTest(unittest.TestCase):
    def testInstanciation(self):
        s = SimpleUseCaseReverse("Hi")
        self.assertEqual(s, "Hi")
        s.setObjectName(s)
        self.assertEqual(s.objectName(), "Hi")

    def testInstanciation2(self):
        s = SimpleUseCase2("Hi")
        self.assertEqual(s, "Hi")
        s.setObjectName(s)
        self.assertEqual(s.objectName(), "Hi")

    def testComplexInstanciation(self):
        # PYSIDE-1564: This test can no longer work because of this MRO:
        # ('ComplexUseCaseReverse', 'Point', 'SimpleUseCase2', 'SimpleUseCase',
        #  'ObjectType', 'Str', 'Object', 'object')
        # By multiple inheritance Point would be called first but has no argument.
        with self.assertRaises(TypeError):
            c = ComplexUseCaseReverse("Hi")
        # c.setObjectName(c)
        # self.assertEqual(c.objectName(), "Hi")
        # c.setX(2);
        # self.assertEqual(c, Point(2, 0))

if __name__ == '__main__':
    unittest.main()
