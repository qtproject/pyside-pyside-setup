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

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QSpinBox, QApplication, QWidget  # noqa: F401

from helper.usesqapplication import UsesQApplication


TEST_LIST = ["item1", "item2", "item3"]


class Sender(QObject):
    """Sender class used in this test."""

    foo = Signal()
    foo_int = Signal(int)
    dummy = Signal(str)
    dummy2 = Signal(str, list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def callDummy(self):
        self.dummy.emit("PyObject")

    def callDummy2(self):
        self.dummy2.emit("PyObject0", TEST_LIST)


class PyObjectType(UsesQApplication):
    def mySlot(self, arg):
        self.assertEqual(arg, "PyObject")
        self.called = True
        self.callCount += 1

    def mySlot2(self, arg0, arg1):
        self.assertEqual(arg0, "PyObject0")
        self.assertEqual(arg1, TEST_LIST)
        self.callCount += 1
        if self.running:
            self.app.quit()

    def setUp(self):
        super().setUp()
        self.callCount = 0
        self.running = False

    def testWithOneArg(self):
        o = Sender()
        o.dummy.connect(self.mySlot)
        o.callDummy()
        self.assertEqual(self.callCount, 1)

    def testWithTwoArg(self):
        o = Sender()
        o.dummy2.connect(self.mySlot2)
        o.callDummy2()
        self.assertEqual(self.callCount, 1)

    def testAsyncSignal(self):
        self.called = False
        self.running = True
        o = Sender()
        o.dummy2.connect(self.mySlot2, Qt.QueuedConnection)
        o.callDummy2()
        self.app.exec()
        self.assertEqual(self.callCount, 1)

    def testTwice(self):
        self.called = False
        self.running = True
        o = Sender()
        o.dummy2.connect(self.mySlot2, Qt.QueuedConnection)
        o.callDummy2()
        o.callDummy2()
        self.app.exec()
        self.assertEqual(self.callCount, 2)


class PythonSigSlot(unittest.TestCase):
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
        """Python signal and slots without arguments"""
        obj1 = Sender()

        obj1.foo.connect(self.callback)
        self.args = tuple()
        obj1.foo.emit(*self.args)

        self.assertTrue(self.called)

    def testWithArgs(self):
        """Python signal and slots with integer arguments"""
        obj1 = Sender()

        obj1.foo_int.connect(self.callback)
        self.args = (42,)
        obj1.foo_int.emit(*self.args)

        self.assertTrue(self.called)

    def testDisconnect(self):
        obj1 = Sender()

        obj1.foo_int.connect(self.callback)
        self.assertTrue(obj1.foo_int.disconnect(self.callback))

        self.args = (42, )
        obj1.foo_int.emit(*self.args)

        self.assertTrue(not self.called)


class SpinBoxPySignal(UsesQApplication):
    """Tests the connection of python signals to QSpinBox qt slots."""

    def setUp(self):
        super().setUp()
        self.obj = Sender()
        self.spin = QSpinBox()
        self.spin.setValue(0)

    def tearDown(self):
        super().tearDown()
        del self.obj
        del self.spin
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testValueChanged(self):
        """Emission of a python signal to QSpinBox setValue(int)"""

        self.obj.foo_int.connect(self.spin.setValue)
        self.assertEqual(self.spin.value(), 0)

        self.obj.foo_int.emit(4)
        self.assertEqual(self.spin.value(), 4)

    def testValueChangedMultiple(self):
        """Multiple emissions of a python signal to QSpinBox setValue(int)"""
        self.obj.foo_int.connect(self.spin.setValue)
        self.assertEqual(self.spin.value(), 0)

        self.obj.foo_int.emit(4)
        self.assertEqual(self.spin.value(), 4)

        self.obj.foo_int.emit(77)
        self.assertEqual(self.spin.value(), 77)


class WidgetPySignal(UsesQApplication):
    """Tests the connection of python signals to QWidget qt slots."""

    def setUp(self):
        super(WidgetPySignal, self).setUp()
        self.obj = Sender()
        self.widget = QWidget()

    def tearDown(self):
        super(WidgetPySignal, self).tearDown()
        del self.obj
        del self.widget
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testShow(self):
        """Emission of a python signal to QWidget slot show()"""
        self.widget.hide()

        self.obj.foo.connect(self.widget.show)
        self.assertTrue(not self.widget.isVisible())

        self.obj.foo.emit()
        self.assertTrue(self.widget.isVisible())


if __name__ == '__main__':
    unittest.main()
