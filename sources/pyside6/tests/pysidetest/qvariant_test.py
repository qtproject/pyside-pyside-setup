# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import TestObject
from PySide6.QtCore import Qt, QKeyCombination
from PySide6.QtGui import QKeySequence, QAction

from helper.usesqapplication import UsesQApplication


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


if __name__ == '__main__':
    unittest.main()
