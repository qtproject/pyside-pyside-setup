#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for type discovery'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import (Abstract, Base1, Derived,
                    MDerived1, SonOfMDerived1, MDerived3)
from other import OtherMultipleDerived


class TypeDiscoveryTest(unittest.TestCase):

    def testPureVirtualsOfImpossibleTypeDiscovery(self):
        a = Derived.triggerImpossibleTypeDiscovery()
        self.assertEqual(type(a), Abstract)
        # call some pure virtual method
        a.pureVirtual()

    def testAnotherImpossibleTypeDiscovery(self):
        a = Derived.triggerAnotherImpossibleTypeDiscovery()
        self.assertEqual(type(a), Derived)

    def testMultipleInheritance(self):
        obj = OtherMultipleDerived.createObject("Base1")
        self.assertEqual(type(obj), Base1)
        # PYSIDE-868: In case of single line direct inheritance,
        # a factory function will return the class wrapper
        # of the derived class.
        obj = OtherMultipleDerived.createObject("MDerived1")
        self.assertEqual(type(obj), MDerived1)
        obj = OtherMultipleDerived.createObject("SonOfMDerived1")
        self.assertEqual(type(obj), SonOfMDerived1)
        obj = OtherMultipleDerived.createObject("MDerived3")
        self.assertEqual(type(obj), MDerived3)
        # PYSIDE-868: OtherMultipleDerived inherits
        # OtherBase, Base1. In this case, a factory
        # function will return the base class wrapper.
        obj = OtherMultipleDerived.createObject("OtherMultipleDerived")
        self.assertEqual(type(obj), Base1)


if __name__ == '__main__':
    unittest.main()
