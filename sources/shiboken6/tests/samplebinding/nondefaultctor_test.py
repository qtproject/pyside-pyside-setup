#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for ...'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import NonDefaultCtor

class DerivedNonDefaultCtor (NonDefaultCtor):
    def returnMyselfVirtual(self):
        return NonDefaultCtor(self.value()+1)

class AnotherDerivedNonDefaultCtor (NonDefaultCtor):
    def __init__(self, some_string):
        pass

class NonDefaultCtorTest(unittest.TestCase):

    def testNonDefaultCtor(self):
        c = NonDefaultCtor(2)
        # these functions returns NonDefaultCtor by value, so a PyObjecy  is created every time
        self.assertNotEqual(c.returnMyself(), c)
        self.assertEqual(c.returnMyself().value(), 2)
        self.assertNotEqual(c.returnMyself(3), c)
        self.assertEqual(c.returnMyself(3).value(), 2)
        self.assertNotEqual(c.returnMyself(4, c), c)
        self.assertEqual(c.returnMyself(4, c).value(), 2)

    def testVirtuals(self):
        c = DerivedNonDefaultCtor(3)
        # these functions returns NonDefaultCtor by value, so a PyObjecy  is created every time
        self.assertNotEqual(c.returnMyselfVirtual(), c)
        self.assertEqual(c.returnMyselfVirtual().value(), 4)
        self.assertEqual(c.callReturnMyselfVirtual().value(), 4)

    def testCtorOverload(self):
        c = AnotherDerivedNonDefaultCtor("testing")

if __name__ == '__main__':
    unittest.main()

