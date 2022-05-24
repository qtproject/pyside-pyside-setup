# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import functools
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Slot, Signal, SIGNAL


def log_exception():
    def log_exception_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except Exception:
                raise

        return wrapper

    return log_exception_decorator


def log_exception2():
    def log_exception_decorator(func):
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except Exception:
                raise

        return wrapper

    return log_exception_decorator


class MyObject(QObject):

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._mySlotcalled = False
        self._mySlot2called = False

    @Slot()
    @log_exception()
    def mySlot(self):
        self._mySlotcalled = True

    @Slot(name="mySlot2")
    @log_exception2()
    def mySlot2(self):
        self._mySlot2called = True

    def poke(self):
        self.events.emit()

    events = Signal()


class SlotWithDecoratorTest(unittest.TestCase):
    def testSlots(self):
        o = MyObject()
        self.assertTrue(o.metaObject().indexOfSlot("mySlot()") > 0)
        self.assertTrue(o.metaObject().indexOfSlot("mySlot2()") > 0)

        o.events.connect(o.mySlot)
        o.events.connect(o.mySlot2)
        o.poke()
        self.assertTrue(o._mySlotcalled)
        self.assertTrue(o._mySlot2called)


if __name__ == '__main__':
    unittest.main()

