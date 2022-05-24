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

from PySide6.QtCore import QObject, SIGNAL, SLOT, Qt

try:
    from PySide6.QtWidgets import QSpinBox, QApplication, QWidget
    hasQtGui = True
except ImportError:
    hasQtGui = False

from helper.usesqapplication import UsesQApplication


class Dummy(QObject):
    """Dummy class used in this test."""
    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def callDummy(self):
        self.emit(SIGNAL("dummy(PyObject)"), "PyObject")

    def callDummy2(self):
        lst = []
        lst.append("item1")
        lst.append("item2")
        lst.append("item3")
        self.emit(SIGNAL("dummy2(PyObject, PyObject)"), "PyObject0", lst)


class PyObjectType(UsesQApplication):
    def mySlot(self, arg):
        self.assertEqual(arg, "PyObject")
        self.called = True
        self.callCount += 1

    def mySlot2(self, arg0, arg1):
        self.assertEqual(arg0, "PyObject0")
        self.assertEqual(arg1[0], "item1")
        self.assertEqual(arg1[1], "item2")
        self.assertEqual(arg1[2], "item3")
        self.callCount += 1
        if self.running:
            self.app.quit()

    def setUp(self):
        super(PyObjectType, self).setUp()
        self.callCount = 0
        self.running = False

    def testWithOneArg(self):
        o = Dummy()
        o.connect(SIGNAL("dummy(PyObject)"), self.mySlot)
        o.callDummy()
        self.assertEqual(self.callCount, 1)

    def testWithTwoArg(self):
        o = Dummy()
        o.connect(SIGNAL("dummy2(PyObject,PyObject)"), self.mySlot2)
        o.callDummy2()
        self.assertEqual(self.callCount, 1)

    def testAsyncSignal(self):
        self.called = False
        self.running = True
        o = Dummy()
        o.connect(SIGNAL("dummy2(PyObject,PyObject)"), self.mySlot2, Qt.QueuedConnection)
        o.callDummy2()
        self.app.exec()
        self.assertEqual(self.callCount, 1)

    def testTwice(self):
        self.called = False
        self.running = True
        o = Dummy()
        o.connect(SIGNAL("dummy2(PyObject,PyObject)"), self.mySlot2, Qt.QueuedConnection)
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
        except:
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def callback(self, *args):
        if tuple(self.args) == args:
            self.called = True

    def testNoArgs(self):
        """Python signal and slots without arguments"""
        obj1 = Dummy()

        QObject.connect(obj1, SIGNAL('foo()'), self.callback)
        self.args = tuple()
        obj1.emit(SIGNAL('foo()'), *self.args)

        self.assertTrue(self.called)

    def testWithArgs(self):
        """Python signal and slots with integer arguments"""
        obj1 = Dummy()

        QObject.connect(obj1, SIGNAL('foo(int)'), self.callback)
        self.args = (42,)
        obj1.emit(SIGNAL('foo(int)'), *self.args)

        self.assertTrue(self.called)

    def testDisconnect(self):
        obj1 = Dummy()

        QObject.connect(obj1, SIGNAL('foo(int)'), self.callback)
        QObject.disconnect(obj1, SIGNAL('foo(int)'), self.callback)

        self.args = (42, )
        obj1.emit(SIGNAL('foo(int)'), *self.args)

        self.assertTrue(not self.called)


if hasQtGui:
    class SpinBoxPySignal(UsesQApplication):
        """Tests the connection of python signals to QSpinBox qt slots."""

        def setUp(self):
            super(SpinBoxPySignal, self).setUp()
            self.obj = Dummy()
            self.spin = QSpinBox()
            self.spin.setValue(0)

        def tearDown(self):
            super(SpinBoxPySignal, self).tearDown()
            del self.obj
            del self.spin
            # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
            gc.collect()

        def testValueChanged(self):
            """Emission of a python signal to QSpinBox setValue(int)"""
            QObject.connect(self.obj, SIGNAL('dummy(int)'), self.spin, SLOT('setValue(int)'))
            self.assertEqual(self.spin.value(), 0)

            self.obj.emit(SIGNAL('dummy(int)'), 4)
            self.assertEqual(self.spin.value(), 4)

        def testValueChangedMultiple(self):
            """Multiple emissions of a python signal to QSpinBox setValue(int)"""
            QObject.connect(self.obj, SIGNAL('dummy(int)'), self.spin, SLOT('setValue(int)'))
            self.assertEqual(self.spin.value(), 0)

            self.obj.emit(SIGNAL('dummy(int)'), 4)
            self.assertEqual(self.spin.value(), 4)

            self.obj.emit(SIGNAL('dummy(int)'), 77)
            self.assertEqual(self.spin.value(), 77)


if hasQtGui:
    class WidgetPySignal(UsesQApplication):
        """Tests the connection of python signals to QWidget qt slots."""

        def setUp(self):
            super(WidgetPySignal, self).setUp()
            self.obj = Dummy()
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

            QObject.connect(self.obj, SIGNAL('dummy()'), self.widget, SLOT('show()'))
            self.assertTrue(not self.widget.isVisible())

            self.obj.emit(SIGNAL('dummy()'))
            self.assertTrue(self.widget.isVisible())

if __name__ == '__main__':
    unittest.main()
