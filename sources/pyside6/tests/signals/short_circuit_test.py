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


class Sender(QObject):
    """Sender class used in this test."""

    foo = Signal()
    foo_int = Signal(int)
    foo_int_int_string = Signal(int, int, str)
    foo_int_qobject = Signal(int, QObject)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)


class ShortCircuitSignals(unittest.TestCase):
    def setUp(self):
        self.called = False

    def tearDown(self):
        try:
            del self.args
        except:  # noqa: E722
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def callback(self, *args):
        if tuple(self.args) == args:
            self.called = True

    def testNoArgs(self):
        """Short circuit signal without arguments"""
        obj1 = Sender()
        obj1.foo.connect(self.callback)
        self.args = tuple()
        obj1.foo.emit(*self.args)
        self.assertTrue(self.called)

    def testWithArgs(self):
        """Short circuit signal with integer arguments"""
        obj1 = Sender()

        obj1.foo_int.connect(self.callback)
        self.args = (42,)
        obj1.foo_int.emit(*self.args)

        self.assertTrue(self.called)

    def testMultipleArgs(self):
        """Short circuit signal with multiple arguments"""
        obj1 = Sender()

        obj1.foo_int_int_string.connect(self.callback)
        self.args = (42, 33, 'char')
        obj1.foo_int_int_string.emit(*self.args)

        self.assertTrue(self.called)

    def testComplexArgs(self):
        """Short circuit signal with complex arguments"""
        obj1 = Sender()

        obj1.foo_int_qobject.connect(self.callback)
        self.args = (42, obj1)

        obj1.foo_int_qobject.emit(*self.args)
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
