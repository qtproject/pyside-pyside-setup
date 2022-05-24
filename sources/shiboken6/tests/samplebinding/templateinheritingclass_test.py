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

from sample import Photon

'''This tests classes that inherit from template classes,
simulating a situation found in Qt's phonon module.'''

class TemplateInheritingClassTest(unittest.TestCase):
    def testClassBasics(self):
        self.assertEqual(Photon.ValueIdentity.classType(), Photon.IdentityType)
        self.assertEqual(Photon.ValueDuplicator.classType(), Photon.DuplicatorType)

    def testInstanceBasics(self):
        value = 123
        samer = Photon.ValueIdentity(value)
        self.assertEqual(samer.multiplicator(), 1)
        doubler = Photon.ValueDuplicator(value)
        self.assertEqual(doubler.multiplicator(), 2)
        self.assertEqual(samer.value(), doubler.value())
        self.assertEqual(samer.calculate() * 2, doubler.calculate())

    def testPassToFunctionAsPointer(self):
        obj = Photon.ValueDuplicator(123)
        self.assertEqual(Photon.callCalculateForValueDuplicatorPointer(obj), obj.calculate())

    def testPassToFunctionAsReference(self):
        obj = Photon.ValueDuplicator(321)
        self.assertEqual(Photon.callCalculateForValueDuplicatorReference(obj), obj.calculate())

    def testPassToMethodAsValue(self):
        value1, value2 = 123, 321
        one = Photon.ValueIdentity(value1)
        other = Photon.ValueIdentity(value2)
        self.assertEqual(one.sumValueUsingPointer(other), value1 + value2)

    def testPassToMethodAsReference(self):
        value1, value2 = 123, 321
        one = Photon.ValueDuplicator(value1)
        other = Photon.ValueDuplicator(value2)
        self.assertEqual(one.sumValueUsingReference(other), value1 + value2)

    def testPassPointerThrough(self):
        obj1 = Photon.ValueIdentity(123)
        self.assertEqual(obj1, obj1.passPointerThrough(obj1))
        obj2 = Photon.ValueDuplicator(321)
        self.assertEqual(obj2, obj2.passPointerThrough(obj2))
        self.assertRaises(TypeError, obj1.passPointerThrough, obj2)

if __name__ == '__main__':
    unittest.main()
