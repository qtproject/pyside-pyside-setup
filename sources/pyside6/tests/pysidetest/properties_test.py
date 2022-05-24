# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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


if __name__ == '__main__':
    unittest.main()
