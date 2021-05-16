# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QTextLayout, QTextOption
from helper.usesqapplication import UsesQApplication


class QTextLineTest(UsesQApplication):

    def testCursorToX(self):
        textLayout = QTextLayout()
        textLayout.beginLayout()
        line = textLayout.createLine()
        self.assertTrue(line.isValid())
        x, cursorPos = line.cursorToX(0)
        self.assertEqual(type(x), float)
        self.assertEqual(type(cursorPos), int)
        x, cursorPos = line.cursorToX(1)
        self.assertEqual(type(x), float)
        self.assertEqual(type(cursorPos), int)

    def testTextOption(self):
        """PYSIDE-2088, large enum values causing MSVC issues."""
        v = QTextOption.IncludeTrailingSpaces | QTextOption.ShowTabsAndSpaces
        self.assertEqual(v.value, 2147483649)


if __name__ == '__main__':
    unittest.main()

