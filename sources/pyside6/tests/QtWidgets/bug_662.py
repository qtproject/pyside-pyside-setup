# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 662: http://bugs.openbossa.org/show_bug.cgi?id=662'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)
from PySide6.QtGui import QTextCharFormat
from PySide6.QtWidgets import QTextEdit, QApplication
import sys


class testQTextBlock(unittest.TestCase):

    def testIterator(self):
        edit = QTextEdit()
        cursor = edit.textCursor()
        fmt = QTextCharFormat()
        frags = []
        for i in range(10):
            fmt.setFontPointSize(i + 10)
            frags.append(f"block{i}")
            cursor.insertText(frags[i], fmt)

        doc = edit.document()
        block = doc.begin()

        index = 0
        for i in block:
            self.assertEqual(i.fragment().text(), frags[index])
            index += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
