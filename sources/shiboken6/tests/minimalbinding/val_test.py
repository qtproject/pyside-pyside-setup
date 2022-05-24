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
from minimal import Val


class ExtVal(Val):
    def __init__(self, valId):
        Val.__init__(self, valId)

    def passValueType(self, val):
        return ExtVal(val.valId() + 1)

    def passValueTypePointer(self, val):
        val.setValId(val.valId() + 1)
        return val

    def passValueTypeReference(self, val):
        val.setValId(val.valId() + 1)
        return val


class ValTest(unittest.TestCase):

    def testNormalMethod(self):
        valId = 123
        val = Val(valId)
        self.assertEqual(val.valId(), valId)

    def testPassValueType(self):
        val = Val(123)
        val1 = val.passValueType(val)
        self.assertNotEqual(val, val1)
        self.assertEqual(val1.valId(), 123)
        val2 = val.callPassValueType(val)
        self.assertNotEqual(val, val2)
        self.assertEqual(val2.valId(), 123)

    def testPassValueTypePointer(self):
        val = Val(0)
        self.assertEqual(val, val.passValueTypePointer(val))
        self.assertEqual(val, val.callPassValueTypePointer(val))

    def testPassValueTypeReference(self):
        val = Val(0)
        self.assertEqual(val, val.passValueTypeReference(val))
        self.assertEqual(val, val.callPassValueTypeReference(val))

    def testPassAndReceiveEnumValue(self):
        val = Val(0)
        self.assertEqual(val.oneOrTheOtherEnumValue(Val.One), Val.Other)
        self.assertEqual(val.oneOrTheOtherEnumValue(Val.Other), Val.One)

    def testPassValueTypeFromExtendedClass(self):
        val = ExtVal(0)
        val1 = val.passValueType(val)
        self.assertNotEqual(val, val1)
        self.assertEqual(val1.valId(), val.valId() + 1)
        val2 = val.callPassValueType(val)
        self.assertNotEqual(val, val2)
        self.assertEqual(val2.valId(), val.valId() + 1)

    def testPassValueTypePointerFromExtendedClass(self):
        val = ExtVal(0)
        self.assertEqual(val.valId(), 0)
        sameVal = val.passValueTypePointer(val)
        self.assertEqual(val, sameVal)
        self.assertEqual(sameVal.valId(), 1)
        sameVal = val.callPassValueTypePointer(val)
        self.assertEqual(val, sameVal)
        self.assertEqual(sameVal.valId(), 2)

    def testPassValueTypeReferenceFromExtendedClass(self):
        val = ExtVal(0)
        self.assertEqual(val.valId(), 0)
        sameVal = val.passValueTypeReference(val)
        self.assertEqual(val, sameVal)
        self.assertEqual(sameVal.valId(), 1)
        sameVal = val.callPassValueTypeReference(val)
        self.assertEqual(val, sameVal)
        self.assertEqual(sameVal.valId(), 2)


if __name__ == '__main__':
    unittest.main()

