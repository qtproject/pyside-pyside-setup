# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''QtTest mouse click functionalities'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QObject
from PySide6.QtWidgets import QPushButton, QLineEdit
from PySide6.QtTest import QTest

from helper.usesqapplication import UsesQApplication


class MouseClickTest(UsesQApplication):

    def testBasic(self):
        '''QTest.mouseClick with QCheckBox'''
        button = QPushButton()
        button.setCheckable(True)
        button.setChecked(False)

        QTest.mouseClick(button, Qt.LeftButton)
        self.assertTrue(button.isChecked())

        QTest.mouseClick(button, Qt.LeftButton)
        self.assertFalse(button.isChecked())


if __name__ == '__main__':
    unittest.main()
