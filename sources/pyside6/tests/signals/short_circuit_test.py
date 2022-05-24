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

from PySide6.QtCore import QObject, SIGNAL, SLOT


class Dummy(QObject):
    """Dummy class used in this test."""
    def __init__(self, parent=None):
        QObject.__init__(self, parent)


class ShortCircuitSignals(unittest.TestCase):
    def setUp(self):
        self.called = False

    def tearDown(self):
        try:
            del self.args
        except:
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def callback(self, *args):
        if tuple(self.args) == args:
            self.called = True

    def testNoArgs(self):
        """Short circuit signal without arguments"""
        obj1 = Dummy()
        QObject.connect(obj1, SIGNAL('foo()'), self.callback)
        self.args = tuple()
        obj1.emit(SIGNAL('foo()'), *self.args)
        self.assertTrue(self.called)

    def testWithArgs(self):
        """Short circuit signal with integer arguments"""
        obj1 = Dummy()

        QObject.connect(obj1, SIGNAL('foo(int)'), self.callback)
        self.args = (42,)
        obj1.emit(SIGNAL('foo(int)'), *self.args)

        self.assertTrue(self.called)

    def testMultipleArgs(self):
        """Short circuit signal with multiple arguments"""
        obj1 = Dummy()

        QObject.connect(obj1, SIGNAL('foo(int,int,QString)'), self.callback)
        self.args = (42, 33, 'char')
        obj1.emit(SIGNAL('foo(int,int,QString)'), *self.args)

        self.assertTrue(self.called)

    def testComplexArgs(self):
        """Short circuit signal with complex arguments"""
        obj1 = Dummy()

        QObject.connect(obj1, SIGNAL('foo(int,QObject*)'), self.callback)
        self.args = (42, obj1)
        obj1.emit(SIGNAL('foo(int,QObject*)'), *self.args)

        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
