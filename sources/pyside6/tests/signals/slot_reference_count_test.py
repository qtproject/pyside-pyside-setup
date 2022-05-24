# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Forced disconnection: Delete one end of the signal connection'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL, SLOT


class Dummy(QObject):
    def dispatch(self):
        self.emit(SIGNAL('foo()'))


class PythonSignalRefCount(unittest.TestCase):

    def setUp(self):
        self.emitter = Dummy()

    def tearDown(self):
        self.emitter

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefCount(self):
        def cb(*args):
            pass

        self.assertEqual(sys.getrefcount(cb), 2)

        QObject.connect(self.emitter, SIGNAL('foo()'), cb)
        self.assertEqual(sys.getrefcount(cb), 3)

        QObject.disconnect(self.emitter, SIGNAL('foo()'), cb)
        self.assertEqual(sys.getrefcount(cb), 2)


class CppSignalRefCount(unittest.TestCase):

    def setUp(self):
        self.emitter = QObject()

    def tearDown(self):
        self.emitter

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefCount(self):
        def cb(*args):
            pass

        self.assertEqual(sys.getrefcount(cb), 2)

        self.emitter.destroyed.connect(cb)
        self.assertEqual(sys.getrefcount(cb), 3)

        QObject.disconnect(self.emitter, SIGNAL('destroyed()'), cb)
        self.assertEqual(sys.getrefcount(cb), 2)


if __name__ == '__main__':
    unittest.main()
