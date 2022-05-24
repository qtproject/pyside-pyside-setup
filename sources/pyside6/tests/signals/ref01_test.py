#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal


class BoundAndUnboundSignalsTest(unittest.TestCase):

    def setUp(self):
        self.methods = set(('connect', 'disconnect', 'emit'))

    def tearDown(self):
        del self.methods
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testUnboundSignal(self):
        self.assertEqual(type(QObject.destroyed), Signal)
        self.assertFalse(self.methods.issubset(dir(QObject.destroyed)))

    def testBoundSignal(self):
        obj = QObject()
        self.assertNotEqual(type(obj.destroyed), Signal)
        self.assertTrue(self.methods.issubset(dir(obj.destroyed)))


if __name__ == '__main__':
    unittest.main()


