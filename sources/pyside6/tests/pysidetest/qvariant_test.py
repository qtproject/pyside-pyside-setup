# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import enum
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import TestObject, TestQVariantEnum
from PySide6.QtCore import Qt, QKeyCombination
from PySide6.QtGui import QKeySequence, QAction

from helper.usesqapplication import UsesQApplication


class PyTestQVariantEnum(TestQVariantEnum):
    def __init__(self, var_enum):
        super().__init__(var_enum)

    def getRValEnum(self):
        return Qt.Orientation.Vertical

    def channelingEnum(self, rval_enum):
        return (isinstance(rval_enum, enum.Enum) and
                rval_enum == Qt.Orientation.Vertical)


class QVariantTest(UsesQApplication):

    def testQKeySequenceQVariantOperator(self):
        # bug #775
        ks = QKeySequence(Qt.ShiftModifier, Qt.ControlModifier, Qt.Key_P, Qt.Key_R)
        self.assertEqual(TestObject.checkType(ks), 4107)

    # PYSIDE-1735: Test the new way to address QKeyCombination after moving IntEnum to Enum
    @unittest.skipUnless(sys.pyside63_option_python_enum, "only implemented for new enums")
    def testQKeySequenceMoreVariations(self):
        QAction().setShortcut(Qt.CTRL | Qt.Key_B)
        QAction().setShortcut(Qt.CTRL | Qt.ALT | Qt.Key_B)
        QAction().setShortcut(Qt.CTRL | Qt.AltModifier | Qt.Key_B)
        QAction().setShortcut(QKeySequence(QKeyCombination(Qt.CTRL | Qt.Key_B)))
        QKeySequence(Qt.CTRL | Qt.Key_Q)
        # Issues a warning but works as well
        QKeySequence(Qt.CTRL + Qt.Key_Q)

    def testEnum(self):
        # Testing C++ class
        testqvariant = TestQVariantEnum(Qt.CheckState.Checked)
        self.assertEqual(testqvariant.getLValEnum(), Qt.CheckState.Checked)
        self.assertIsInstance(testqvariant.getLValEnum(), enum.Enum)
        # in the case where we return a QVariant of C++ enum, it returns a
        # QVariant(int) to Python unless explicitly handled manually by Shiboken
        self.assertEqual(testqvariant.getRValEnum(), 1)
        self.assertEqual(testqvariant.isEnumChanneled(), False)

        # Testing Python child class
        pytestqvariant = PyTestQVariantEnum(Qt.CheckState.Checked)
        self.assertEqual(pytestqvariant.isEnumChanneled(), True)
        # check toInt() conversion works for PyObjectWrapper
        self.assertEqual(PyTestQVariantEnum.getNumberFromQVarEnum(Qt.Orientation.Vertical), 2)
        # check toInt() conversion for IntEnum
        self.assertEqual(PyTestQVariantEnum.getNumberFromQVarEnum(Qt.GestureType.TapGesture), 1)


if __name__ == '__main__':
    unittest.main()
