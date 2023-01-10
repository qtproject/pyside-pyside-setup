#!/usr/bin/env python
# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from minimal import ContainerUser


class ContainerTest(unittest.TestCase):
    """Simple test for converting std::vector and using an opaque container.
        For advanced tests, see ListUser."""
    def testVectorConversion(self):
        v = ContainerUser.createIntVector(4)
        self.assertEqual(ContainerUser.sumIntVector(v), 6)

    def testVectorOpaqueContainer(self):
        cu = ContainerUser()
        oc = cu.intVector()
        self.assertEqual(oc[0], 1)
        oc[0] = 42
        self.assertEqual(cu.intVector()[0], 42)

    def testArrayConversion(self):
        v = ContainerUser.createIntArray()
        self.assertEqual(ContainerUser.sumIntArray(v), 6)

    def testArrayOpaqueContainer(self):
        cu = ContainerUser()
        oc = cu.intArray()
        self.assertEqual(oc[0], 1)
        oc[0] = 42
        self.assertEqual(cu.intArray()[0], 42)


if __name__ == '__main__':
    unittest.main()
