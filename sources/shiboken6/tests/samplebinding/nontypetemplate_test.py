#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

hasNumPy = False

try:
    import numpy
    hasNumPy = True
except ImportError:
    pass

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import IntArray2, IntArray3

class NonTypeTemplateTest(unittest.TestCase):

    def testNonTypeTemplate(self):
        array2 = IntArray2(3)
        self.assertEqual(array2.sum(), 6)
        array3 = IntArray3(5)
        self.assertEqual(array3.sum(), 15)

    def testArrayInitializer(self):
        if not hasNumPy:
            return
        array3 = IntArray3(numpy.array([1, 2, 3], dtype = 'int32'))
        self.assertEqual(array3.sum(), 6)


if __name__ == '__main__':
    unittest.main()
