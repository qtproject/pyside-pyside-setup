#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for OddBool user's primitive type conversion.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import OddBoolUser, ComparisonTester, SpaceshipComparisonTester

class DerivedOddBoolUser (OddBoolUser):
    def returnMyselfVirtual(self):
        return OddBoolUser()
    pass

class OddBoolTest(unittest.TestCase):

    def testOddBoolUser(self):
        obuTrue = OddBoolUser()
        obuFalse = OddBoolUser()
        obuTrue.setOddBool(True)
        self.assertEqual(obuFalse.oddBool(), False)
        self.assertEqual(obuTrue.oddBool(), True)
        self.assertEqual(obuTrue.callInvertedOddBool(), False)

        self.assertEqual(obuTrue.oddBool() == True, True)
        self.assertEqual(False == obuFalse.oddBool(), True)
        self.assertEqual(obuTrue.oddBool() == obuFalse.oddBool(), False)

        self.assertEqual(obuFalse.oddBool() != True, True)
        self.assertEqual(True != obuFalse.oddBool(), True)
        self.assertEqual(obuTrue.oddBool() != obuFalse.oddBool(), True)

    def testVirtuals(self):
        dobu = DerivedOddBoolUser()
        self.assertEqual(dobu.invertedOddBool(), True)

    def testImplicitConversionWithUsersPrimitiveType(self):
        obu = OddBoolUser(True)
        self.assertTrue(obu.oddBool())
        obu = OddBoolUser(False)
        self.assertFalse(obu.oddBool())
        cpx = complex(1.0, 0.0)
        obu = OddBoolUser(cpx)
        self.assertTrue(obu.oddBool())
        cpx = complex(0.0, 0.0)
        obu = OddBoolUser(cpx)
        self.assertFalse(obu.oddBool())

    def testOddOperators(self):
        t1 = ComparisonTester(42)
        t2 = ComparisonTester(42)
        self.assertEqual(t1, t2)

    def testSpaceshipOperator(self):
        if not SpaceshipComparisonTester.HasSpaceshipOperator:
            print("Skipping Spaceship Operator test")
            return
        t1 = SpaceshipComparisonTester(42)
        t2 = SpaceshipComparisonTester(42)
        self.assertEqual(t1, t2)
        self.assertTrue(t1 <= t2)
        self.assertTrue(t1 >= t2)
        t2 = SpaceshipComparisonTester(43)
        self.assertTrue(t1 < t2)
        self.assertFalse(t1 > t2)


if __name__ == '__main__':
    unittest.main()
