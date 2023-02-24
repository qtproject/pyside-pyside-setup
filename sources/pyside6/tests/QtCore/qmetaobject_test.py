#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for static methos conflicts with class methods'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import (QCoreApplication, QFile, QMetaMethod, QMetaObject,
                            QObject, QModelIndex, QPoint, QTimer, QSemaphore,
                            QStringListModel, Qt, Signal, Slot,
                            SIGNAL, Q_ARG, Q_RETURN_ARG)


class Foo(QFile):
    pass


class DynObject(QObject):
    def slot(self):
        pass


class InvokeTester(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(int, int, result=int)
    def add(self, a, b):
        return a + b

    @Slot(str, str, result=str)
    def concatenate(self, a, b):
        return a + b

    @Slot(QPoint, result=int)
    def manhattan_length(self, point):
        return abs(point.x()) + abs(point.y())

    @Slot(QPoint, QPoint, result=QPoint)
    def add_points(self, point1, point2):
        return point1 + point2

    @Slot(QObject, result=str)
    def object_name(self, o):
        return o.objectName()

    @Slot(QObject, result=QObject)
    def first_child(self, o):
        return o.children()[0]


class SemaphoreSender(QObject):
    signal = Signal(QSemaphore)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.semaphore = QSemaphore()

    def emitSignal(self):
        self.signal.emit(self.semaphore)


class SemaphoreReceiver(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.semaphore = None

    @Slot(QSemaphore)
    def receiverSlot(self, semaphore):
        self.semaphore = semaphore


class qmetaobject_test(unittest.TestCase):
    """
    def test_QMetaObject(self):
        qobj = QObject()
        qobj_metaobj = qobj.metaObject()
        self.assertEqual(qobj_metaobj.className(), "QObject")

        obj = QFile()
        m = obj.metaObject()
        self.assertEqual(m.className(), "QFile")
        self.assertNotEqual(m.methodCount(), qobj_metaobj.methodCount())

        obj = Foo()
        m = obj.metaObject()
        self.assertEqual(m.className(), "Foo")
        f = QFile()
        fm = f.metaObject()
        self.assertEqual(m.methodCount(), fm.methodCount())
    """

    def test_DynamicSlotSignal(self):
        o = DynObject()
        o2 = QObject()

        o.connect(o2, SIGNAL("bars()"), o.slot)
        self.assertTrue(o2.metaObject().indexOfMethod("bars()") > -1)
        #self.assertTrue(o.metaObject().indexOfMethod("bar()") == -1)
        #self.assertTrue(o.metaObject().indexOfMethod("slot()") > -1)

        #slot_index = o.metaObject().indexOfMethod("slot()")

        #o.connect(o, SIGNAL("foo()"), o2, SIGNAL("bar()"))
        #signal_index = o.metaObject().indexOfMethod("foo()");

        #self.assertTrue(slot_index != signal_index)

    # PYSIDE-784, plain Qt objects should not have intermediary
    # metaObjects.
    def test_PlainQObject(self):
        timer = QTimer()
        self.assertEqual(timer.metaObject().superClass().className(),
                         "QObject")

    # PYSIDE-1827, slots with non-QObject object types should work
    # (metatypes are registered)
    def test_ObjectSlotSignal(self):
        app = QCoreApplication()
        sender = SemaphoreSender()
        receiver = SemaphoreReceiver()
        sender.signal.connect(receiver.receiverSlot, Qt.QueuedConnection)
        sender.emitSignal()
        while not receiver.semaphore:
            QCoreApplication.processEvents()
        self.assertEqual(sender.semaphore, receiver.semaphore)

    # PYSIDE-1898,
    def test_Invoke(self):
        tester = InvokeTester()

        # Primitive types
        sum = QMetaObject.invokeMethod(tester, "add", Q_RETURN_ARG(int),
                                       Q_ARG(int, 2), Q_ARG(int, 3))
        self.assertEqual(sum, 5)

        concatenated = QMetaObject.invokeMethod(tester, "concatenate",
                                                Q_RETURN_ARG(str),
                                                Q_ARG(str, "bla"),
                                                Q_ARG(str, "bla"))
        self.assertEqual(concatenated, "blabla")

        # Wrapped type as in-parameter
        point = QPoint(10, 20)
        len = QMetaObject.invokeMethod(tester, "manhattan_length",
                                       Q_RETURN_ARG(int),
                                       Q_ARG(QPoint, point))
        self.assertEqual(len, point.manhattanLength())

        # Wrapped type as result
        point2 = QPoint(30, 30)
        point3 = QMetaObject.invokeMethod(tester, "add_points",
                                          Q_RETURN_ARG(QPoint),
                                          Q_ARG(QPoint, point),
                                          Q_ARG(QPoint, point2))
        self.assertEqual(point + point2, point3)

        # Pass an object
        o = QObject()
        o.setObjectName("Foo")
        name = QMetaObject.invokeMethod(tester, "object_name",
                                        Q_RETURN_ARG(str),
                                        Q_ARG(QObject, o))
        self.assertEqual(name, o.objectName())

        # Return an object
        child = QObject(o)
        child.setObjectName("Child")
        c = QMetaObject.invokeMethod(tester, "first_child",
                                     Q_RETURN_ARG(QObject),
                                     Q_ARG(QObject, o))
        self.assertTrue(c)
        self.assertEqual(c, child)

    def test_InvokeTypeString(self):
        strings = ["item1", "item2"]
        model = QStringListModel(strings)
        index = model.index(1, 0)
        QMetaObject.invokeMethod(model, "setData",
                                 Q_ARG(QModelIndex, index),
                                 Q_ARG("QVariant", "bla"))
        self.assertEqual(model.data(index), "bla")

    def test_QMetaMethod(self):
        o = QObject()
        m = QMetaMethod.fromSignal(o.destroyed)
        self.assertTrue(m.isValid)
        self.assertEqual(m.methodSignature(), b"destroyed()")


if __name__ == '__main__':
    unittest.main()
