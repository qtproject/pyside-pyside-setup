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

from PySide6.QtCore import QTimer, QObject, Signal


class TestDestroySignal(unittest.TestCase):
    def onObjectDestroyed(self, timer):
        self.assertTrue(isinstance(timer, QObject))
        self._destroyed = True

    def testSignal(self):
        self._destroyed = False
        t = QTimer()
        t.destroyed[QObject].connect(self.onObjectDestroyed)
        del t
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertTrue(self._destroyed)

    def testWithParent(self):
        self._destroyed = False
        p = QTimer()
        t = QTimer(p)
        t.destroyed[QObject].connect(self.onObjectDestroyed)
        del p
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertTrue(self._destroyed)


class Foo(QObject):
    s = Signal(int)

    def __init__(self):
        QObject.__init__(self)
        sys.stderr.write(f"__init__ {id(self):x}\n")

    def __del__(self):
        sys.stderr.write(f"__del__  {id(self):x}\n")

    def send(self, i):
        self.s.emit(i)


# PYSIDE-2201/2328: This crashed until we introduced a weak reference.
class TestDestroyNoConnect(unittest.TestCase):

    def testSignalDestroyedMissingReference(self):
        # This works since it has one reference more to Foo
        Foo().send(43)
        # This crashed because we have no reference in the signal.
        with self.assertRaises(RuntimeError):
            Foo().s.emit(44)

    def testSignalDestroyedinConnect(self):
        # PYSIDE-2328: Connect to signal of temporary
        with self.assertRaises(RuntimeError):
            Foo().s.connect(None)


if __name__ == '__main__':
    unittest.main()

