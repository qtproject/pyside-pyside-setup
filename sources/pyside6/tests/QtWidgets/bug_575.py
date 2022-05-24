# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

""" Unittest for bug #575 """
""" http://bugs.openbossa.org/show_bug.cgi?id=575 """

import sys
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QPlainTextEdit, QTextEdit


class Bug575(unittest.TestCase):
    def testPropertyValues(self):
        app = QApplication(sys.argv)
        textEdit = QPlainTextEdit()
        textEdit.insertPlainText("PySide INdT")
        selection = QTextEdit.ExtraSelection()
        selection.cursor = textEdit.textCursor()
        selection.cursor.setPosition(2)
        self.assertEqual(selection.cursor.position(), 2)


if __name__ == '__main__':
    unittest.main()

