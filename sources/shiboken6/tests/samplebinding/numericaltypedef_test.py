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

from sample import SizeF

class NumericalTypedefTest(unittest.TestCase):

    def testNumericalTypedefExact(self):
        width, height = (1.1, 2.2)
        size = SizeF(width, height)
        self.assertEqual(size.width(), width)
        self.assertEqual(size.height(), height)

    def testNumericalTypedefConvertible(self):
        width, height = (1, 2)
        size = SizeF(width, height)
        self.assertEqual(size.width(), float(width))
        self.assertEqual(size.height(), float(height))

    def testNumericalTypedefOfUnsignedShort(self):
        self.assertEqual(SizeF.passTypedefOfUnsignedShort(123), 123)
        self.assertEqual(SizeF.passTypedefOfUnsignedShort(321), 321)
        self.assertNotEqual(SizeF.passTypedefOfUnsignedShort(123), 0)

if __name__ == '__main__':
    unittest.main()
