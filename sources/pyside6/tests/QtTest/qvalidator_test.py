# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QLineEdit
from PySide6.QtTest import QTest
from helper.usesqapplication import UsesQApplication


class MyValidator1(QValidator):
    def fixup(self, input):
        return "fixed"

    def validate(self, input, pos):
        return (QValidator.Acceptable, "fixed", 1)


class MyValidator2(QValidator):
    def fixup(self, input):
        return "fixed"

    def validate(self, input, pos):
        return (QValidator.Acceptable, "fixed")


class MyValidator3(QValidator):
    def fixup(self, input):
        return "fixed"

    def validate(self, input, pos):
        return (QValidator.Acceptable,)


class MyValidator4(QValidator):
    def fixup(self, input):
        return "fixed"

    def validate(self, input, pos):
        return QValidator.Acceptable


class MyValidator5(QValidator):
    def validate(self, input, pos):
        if input.islower():
            return (QValidator.Intermediate, input, pos)
        else:
            return (QValidator.Acceptable, input, pos)

    def fixup(self, input):
        return "22"


class QValidatorTest(UsesQApplication):
    def testValidator1(self):
        line = QLineEdit()
        line.setValidator(MyValidator1())
        line.show()
        line.setText("foo")

        QTimer.singleShot(0, line.close)
        self.app.exec()

        self.assertEqual(line.text(), "fixed")
        self.assertEqual(line.cursorPosition(), 1)

    def testValidator2(self):
        line = QLineEdit()
        line.setValidator(MyValidator2())
        line.show()
        line.setText("foo")

        QTimer.singleShot(0, line.close)
        self.app.exec()

        self.assertEqual(line.text(), "fixed")
        self.assertEqual(line.cursorPosition(), 3)

    def testValidator3(self):
        line = QLineEdit()
        line.setValidator(MyValidator3())
        line.show()
        line.setText("foo")

        QTimer.singleShot(0, line.close)
        self.app.exec()

        self.assertEqual(line.text(), "foo")
        self.assertEqual(line.cursorPosition(), 3)

    def testValidator4(self):
        line = QLineEdit()
        line.setValidator(MyValidator4())
        line.show()
        line.setText("foo")

        QTimer.singleShot(0, line.close)
        self.app.exec()

        self.assertEqual(line.text(), "foo")
        self.assertEqual(line.cursorPosition(), 3)

    def testValidator5(self):
        line = QLineEdit()
        line.show()
        line.setValidator(MyValidator5())
        line.setText("foo")
        QTest.keyClick(line, Qt.Key_Return)
        self.assertEqual(line.text(), "22")


if __name__ == '__main__':
    unittest.main()
