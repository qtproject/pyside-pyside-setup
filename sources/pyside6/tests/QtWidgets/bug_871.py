# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtGui import QValidator, QIntValidator
from PySide6.QtWidgets import QLineEdit

'''Bug #871 - http://bugs.pyside.org/show_bug.cgi?id=871'''


class BlankIntValidator(QIntValidator):
    def validate(self, input, pos):
        if input == '':
            return QValidator.Acceptable, input, pos
        else:
            return QIntValidator.validate(self, input, pos)


class Bug871Test(UsesQApplication):
    def testWithoutValidator(self):
        edit = QLineEdit()
        self.assertEqual(edit.text(), '')
        edit.insert('1')
        self.assertEqual(edit.text(), '1')
        edit.insert('a')
        self.assertEqual(edit.text(), '1a')
        edit.insert('2')
        self.assertEqual(edit.text(), '1a2')

    def testWithIntValidator(self):
        edit = QLineEdit()
        edit.setValidator(BlankIntValidator(edit))
        self.assertEqual(edit.text(), '')
        edit.insert('1')
        self.assertEqual(edit.text(), '1')
        edit.insert('a')
        self.assertEqual(edit.text(), '1')
        edit.insert('2')
        self.assertEqual(edit.text(), '12')


if __name__ == "__main__":
    unittest.main()

