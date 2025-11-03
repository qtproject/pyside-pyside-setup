# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QStringListModel, Signal, Property, Slot

"""Tests PySide6.QtCore.Property()"""


class TestObject(QObject):

    valueChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = -1
        self.valueChanged.connect(self._changed)
        self.getter_called = 0
        self.setter_called = 0
        self.changed_emitted = 0

    @Slot(int)
    def _changed(self):
        self.changed_emitted += 1

    def getValue(self):
        self.getter_called += 1
        return self._value

    def setValue(self, value):
        self.setter_called += 1
        if (self._value != value):
            self._value = value
            self.valueChanged.emit()

    value = Property(int, fget=getValue, fset=setValue,
                     notify=valueChanged)


class TestDerivedObject(QStringListModel):

    valueChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = -1
        self.valueChanged.connect(self._changed)
        self.getter_called = 0
        self.setter_called = 0
        self.changed_emitted = 0

    @Slot(int)
    def _changed(self):
        self.changed_emitted += 1

    def getValue(self):
        self.getter_called += 1
        return self._value

    def setValue(self, value):
        self.setter_called += 1
        if (self._value != value):
            self._value = value
            self.valueChanged.emit()

    value = Property(int, fget=getValue, fset=setValue,
                     notify=valueChanged)


class SpecialProperties(QObject):
    _value = 1

    def __init__(self):
        super().__init__()
        self._readWriteInt = 2
        self._readWriteDecoratedInt = 3

    def readOnlyInt(self):  # Class variable properties
        return 4

    def readWriteInt(self):
        return self._readWriteInt

    def setReadWriteInt(self, v):
        self._readWriteInt = v

    @Property(int)  # Property decorators
    def readOnlyDecoratedInt(self):
        return 5

    @Property(int)
    def readWriteDecoratedInt(self):
        return self._readWriteDecoratedInt

    @readWriteDecoratedInt.setter
    def readWriteDecoratedInt(self, v):
        self._readWriteDecoratedInt = v

    constantValue = Property(int, lambda self: self._value, constant=True)
    readOnlyInt = Property(int, readOnlyInt)
    readWriteInt = Property(int, readWriteInt, fset=setReadWriteInt)


class PropertyTest(unittest.TestCase):

    def test1Object(self):
        """Basic property test."""
        testObject = TestObject()
        v = testObject.value
        self.assertEqual(v, -1)
        self.assertEqual(testObject.getter_called, 1)
        testObject.value = 42
        v = testObject.value
        self.assertEqual(v, 42)
        self.assertEqual(testObject.changed_emitted, 1)
        self.assertEqual(testObject.setter_called, 1)
        self.assertEqual(testObject.getter_called, 2)

    def test2DerivedObject(self):
        """PYSIDE-1255: Run the same test for a class inheriting QObject."""
        testObject = TestDerivedObject()
        v = testObject.value
        self.assertEqual(v, -1)
        self.assertEqual(testObject.getter_called, 1)
        testObject.value = 42
        v = testObject.value
        self.assertEqual(v, 42)
        self.assertEqual(testObject.changed_emitted, 1)
        self.assertEqual(testObject.setter_called, 1)
        self.assertEqual(testObject.getter_called, 2)

    def testSpecialProperties(self):
        """PYSIDE-924, PYSIDE-3227, constant, read-only."""
        testObject = SpecialProperties()
        mo = testObject.metaObject()

        i = mo.indexOfProperty("constantValue")
        self.assertTrue(i != -1)
        metaProperty = mo.property(i)
        self.assertTrue(metaProperty.isConstant())
        self.assertEqual(testObject.constantValue, 1)

        i = mo.indexOfProperty("readWriteInt")
        self.assertTrue(i != -1)
        metaProperty = mo.property(i)
        self.assertTrue(metaProperty.isWritable())
        self.assertEqual(testObject.readWriteInt, 2)
        testObject.readWriteInt = 42
        self.assertEqual(testObject.readWriteInt, 42)

        i = mo.indexOfProperty("readWriteDecoratedInt")
        self.assertTrue(i != -1)
        metaProperty = mo.property(i)
        self.assertTrue(metaProperty.isWritable())
        self.assertEqual(testObject.readWriteDecoratedInt, 3)
        testObject.readWriteDecoratedInt = 42
        self.assertEqual(testObject.readWriteDecoratedInt, 42)

        i = mo.indexOfProperty("readOnlyInt")
        self.assertTrue(i != -1)
        metaProperty = mo.property(i)
        self.assertFalse(metaProperty.isWritable())
        self.assertEqual(testObject.readOnlyInt, 4)
        with self.assertRaises(AttributeError):
            testObject.readOnlyInt = 42

        i = mo.indexOfProperty("readOnlyDecoratedInt")
        self.assertTrue(i != -1)
        metaProperty = mo.property(i)
        self.assertFalse(metaProperty.isWritable())
        self.assertEqual(testObject.readOnlyDecoratedInt, 5)
        with self.assertRaises(AttributeError):
            testObject.readOnlyDecoratedInt = 42


if __name__ == '__main__':
    unittest.main()
