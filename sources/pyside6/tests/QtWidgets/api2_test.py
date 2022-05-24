# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for PySide API2 support'''


import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QIntValidator, QValidator
from PySide6.QtWidgets import QWidget, QSpinBox, QApplication

from helper.usesqapplication import UsesQApplication


class WidgetValidatorQInt(QWidget, QIntValidator):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        QIntValidator.__init__(self, parent)


class WidgetValidatorQSpinBox(QSpinBox):
    def __init__(self, parent=None):
        QSpinBox.__init__(self, parent)

    def fixup(self, text):
        print("It was called!")


class DoubleQObjectInheritanceTest(UsesQApplication):

    def testDouble(self):
        '''Double inheritance from QObject classes'''

        obj = WidgetValidatorQInt()

        # QIntValidator methods
        state, string, number = obj.validate('Test', 0)
        self.assertEqual(state, QValidator.Invalid)
        state, string, number = obj.validate('33', 0)
        self.assertEqual(state, QValidator.Acceptable)

    def testQSpinBox(self):
        obj = WidgetValidatorQSpinBox()

        obj.setRange(1, 10)
        obj.setValue(0)
        self.assertEqual(obj.value(), 1)


class QClipboardTest(UsesQApplication):

    def testQClipboard(self):
        # skip this test on macOS because the clipboard is not available during the ssh session
        # this cause problems in the buildbot
        if sys.platform == 'darwin':
            return
        clip = QApplication.clipboard()
        clip.setText("Testing this thing!")

        text, subtype = clip.text("")
        self.assertEqual(subtype, "plain")
        self.assertEqual(text, "Testing this thing!")


if __name__ == '__main__':
    unittest.main()
