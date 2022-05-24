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

from minimal import MinBoolUser

class DerivedMinBoolUser (MinBoolUser):
    def returnMyselfVirtual(self):
        return MinBoolUser()

class MinBoolTest(unittest.TestCase):

    def testMinBoolUser(self):
        mbuTrue = MinBoolUser()
        mbuFalse = MinBoolUser()
        mbuTrue.setMinBool(True)
        self.assertEqual(mbuFalse.minBool(), False)
        self.assertEqual(mbuTrue.minBool(), True)
        self.assertEqual(mbuTrue.callInvertedMinBool(), False)

        self.assertEqual(mbuTrue.minBool() == True, True)
        self.assertEqual(False == mbuFalse.minBool(), True)
        self.assertEqual(mbuTrue.minBool() == mbuFalse.minBool(), False)

        self.assertEqual(mbuFalse.minBool() != True, True)
        self.assertEqual(True != mbuFalse.minBool(), True)
        self.assertEqual(mbuTrue.minBool() != mbuFalse.minBool(), True)

    def testVirtuals(self):
        dmbu = DerivedMinBoolUser()
        self.assertEqual(dmbu.invertedMinBool(), True)

if __name__ == '__main__':
    unittest.main()

