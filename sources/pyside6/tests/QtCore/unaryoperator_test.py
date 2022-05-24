#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests the presence of unary operator __neg__ on the QPoint class'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QPoint


class NegUnaryOperatorTest(unittest.TestCase):
    '''Tests the presence of unary operator __neg__ on the QPoint class'''

    def setUp(self):
        # Acquire resources
        self.x, self.y = 10, 20
        self.neg_x, self.neg_y = -self.x, -self.y
        self.qpoint = QPoint(self.x, self.y)

    def tearDown(self):
        # Release resources
        del self.qpoint
        del self.x
        del self.y
        del self.neg_x
        del self.neg_y
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testNegUnaryOperator(self):
        # Test __neg__ unary operator on QPoint class
        __neg__method_exists = True
        try:
            neg_qpoint = -self.qpoint
        except:
            __neg__method_exists = False

        self.assertTrue(__neg__method_exists)
        self.assertEqual(self.qpoint, -neg_qpoint)


if __name__ == '__main__':
    unittest.main()

