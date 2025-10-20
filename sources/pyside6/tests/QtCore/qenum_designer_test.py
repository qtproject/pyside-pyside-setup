#!/usr/bin/python
# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QEnum and QFlags within Qt Widgets Designer'''

import os
import sys
import unittest

from enum import Enum, Flag

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Property, QEnum, QFlag, Qt


class CustomWidgetBase(QObject):
    @QEnum
    class TestEnum(Enum):
        EnumValue0 = 0
        EnumValue1 = 1
        EnumValue2 = 2
        EnumValue3 = 3

    @QFlag
    class TestFlag(Flag):
        FlagValue0 = 1
        FlagValue1 = 2
        FlagValue2 = 4
        FlagValue3 = 8

    @QFlag
    class BigTestFlag(Flag):
        BigFlagValue0 = 0x100000000  # >32bit
        BigFlagValue1 = 0x200000000
        BigFlagValue2 = 0x400000000
        BigFlagValue3 = 0x800000000


class CustomWidget(CustomWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._testEnum = CustomWidget.TestEnum.EnumValue1
        self._testFlag = (CustomWidget.TestFlag.FlagValue0
                          | CustomWidget.TestFlag.FlagValue1)
        self._bigTestFlag = CustomWidget.BigTestFlag.BigFlagValue1
        self._orientation = Qt.Orientation.Horizontal

    def orientation(self):
        return self._orientation

    def setOrientation(self, new_val):
        self._orientation = new_val

    def testEnum(self):
        return self._testEnum

    def setTestEnum(self, new_val):
        self._testEnum = new_val

    def getTestFlag(self):
        return self._testFlag

    def setTestFlag(self, new_val):
        self._testFlag = new_val

    def getBigTestFlag(self):
        return self._bigTestFlag

    def setBigTestFlag(self, new_val):
        self._bigTestFlag = new_val

    # Qt C++ enum
    orientation = Property(Qt.Orientation, orientation, setOrientation)
    # Decorated Python enums
    testEnum = Property(CustomWidgetBase.TestEnum, testEnum, setTestEnum)
    testFlag = Property(CustomWidgetBase.TestFlag, getTestFlag, setTestFlag)
    bigTestFlag = Property(CustomWidgetBase.BigTestFlag,
                           getBigTestFlag, setBigTestFlag)


class TestDesignerEnum(unittest.TestCase):
    """PYSIDE-2840: Test whether a custom widget with decorated enum/flag properties
       allows for modifying the values from C++."""

    def setUp(self):
        super().setUp()
        self._cw = CustomWidget()

    def tearDown(self):
        super().tearDown()
        self._cw = None

    def testEnum(self):
        # Emulate Qt Widgets Designer setting a property
        cw = self._cw
        cw.setProperty("testEnum", 3)
        self.assertEqual(cw.testEnum, CustomWidget.TestEnum.EnumValue3)
        # Emulate uic generated code
        cw.setProperty("testEnum", CustomWidgetBase.TestEnum.EnumValue2)
        self.assertEqual(cw.testEnum, CustomWidget.TestEnum.EnumValue2)

        # Emulate Qt Widgets Designer setting a property
        cw.setProperty("testFlag", 12)
        self.assertEqual(cw.testFlag, (CustomWidget.TestFlag.FlagValue2
                                       | CustomWidget.TestFlag.FlagValue3))
        # Emulate uic generated code
        cw.setProperty("testFlag", CustomWidgetBase.TestFlag.FlagValue1)
        self.assertEqual(cw.testFlag, CustomWidget.TestFlag.FlagValue1)

        # Emulate Qt Widgets Designer setting a property (note though
        # it does not support it).
        self.assertEqual(cw.bigTestFlag, CustomWidget.BigTestFlag.BigFlagValue1)
        ok = cw.setProperty("bigTestFlag", CustomWidgetBase.BigTestFlag.BigFlagValue2)
        self.assertTrue(ok)
        self.assertEqual(cw.bigTestFlag, CustomWidget.BigTestFlag.BigFlagValue2)

    def testMetaProperty(self):
        mo = self._cw.metaObject()
        index = mo.indexOfProperty("orientation")
        self.assertTrue(index != -1)
        self.assertTrue(mo.property(index).isEnumType())
        index = mo.indexOfProperty("testEnum")
        self.assertTrue(index != -1)
        self.assertTrue(mo.property(index).isEnumType())
        index = mo.indexOfProperty("testFlag")
        self.assertTrue(index != -1)
        self.assertTrue(mo.property(index).isEnumType())


if __name__ == '__main__':
    unittest.main()
