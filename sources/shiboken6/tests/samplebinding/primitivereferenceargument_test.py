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
import sample

class PrimitiveReferenceArgumentTest(unittest.TestCase):

    def testIntReferenceArgument(self):
        '''C++ signature: int acceptIntReference(int&)'''
        self.assertEqual(sample.acceptIntReference(123), 123)

    def testIntReturnPtr(self):
        '''C++ signature: const int *acceptIntReturnPtr(int x)'''
        self.assertEqual(sample.acceptIntReturnPtr(123), 123)

    def testOddBoolReferenceArgument(self):
        '''C++ signature: OddBool acceptOddBoolReference(OddBool&)'''
        self.assertEqual(sample.acceptOddBoolReference(True), True)
        self.assertEqual(sample.acceptOddBoolReference(False), False)
        self.assertNotEqual(sample.acceptOddBoolReference(True), False)
        self.assertNotEqual(sample.acceptOddBoolReference(False), True)

if __name__ == '__main__':
    unittest.main()
