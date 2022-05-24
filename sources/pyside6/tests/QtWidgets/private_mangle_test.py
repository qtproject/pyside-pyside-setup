# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
This is the example from https://bugreports.qt.io/browse/PYSIDE-772
with no interaction as a unittest.
"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget
from PySide6 import QtWidgets


class Harness(QWidget):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.clicked.connect(self.method)
        self.clicked.connect(self._method)
        self.clicked.connect(self.__method)

    def method(self):  # Public method
        self.method_result = self.sender()

    def _method(self):  # Private method
        self.method__result = self.sender()

    def __method(self):  # Name mangled method
        self.method___result = self.sender()


class _Under(QWidget):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.clicked.connect(self.method)
        self.clicked.connect(self._method)
        self.clicked.connect(self.__method)

    def method(self):  # Public method
        self.method_result = self.sender()

    def _method(self):  # Private method
        self.method__result = self.sender()

    def __method(self):  # Name mangled method
        self.method___result = self.sender()


class TestMangle(unittest.TestCase):

    def setUp(self):
        QApplication()

    def tearDown(self):
        qApp.shutdown()

    def testPrivateMangle(self):
        harness = Harness()
        harness.clicked.emit()
        self.assertEqual(harness.method_result, harness)
        self.assertEqual(harness.method__result, harness)
        self.assertEqual(harness.method___result, harness)
        self.assertTrue("method" in type(harness).__dict__)
        self.assertTrue("_method" in type(harness).__dict__)
        self.assertFalse("__method" in type(harness).__dict__)
        self.assertTrue("_Harness__method" in type(harness).__dict__)

    def testPrivateMangleUnder(self):
        harness = _Under()
        harness.clicked.emit()
        self.assertEqual(harness.method_result, harness)
        self.assertEqual(harness.method__result, harness)
        self.assertEqual(harness.method___result, harness)
        # make sure that we skipped over the underscore in "_Under"
        self.assertTrue("method" in type(harness).__dict__)
        self.assertTrue("_method" in type(harness).__dict__)
        self.assertFalse("__method" in type(harness).__dict__)
        self.assertTrue("_Under__method" in type(harness).__dict__)


if __name__ == '__main__':
    unittest.main()
