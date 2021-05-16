# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QFont
from helper.usesqapplication import UsesQApplication


class QFontTest(UsesQApplication):

    def testStringConstruction(self):
        """PYSIDE-1685: Test that passing str to QFont works after addding
           QFont(QStringList) by qtbase/d8602ce58b6ef268be84b9aa0166b0c3fa6a96e8"""
        font_name = 'Times Roman'
        font = QFont(font_name)
        families = font.families()
        self.assertEqual(len(families), 1)
        self.assertEqual(families[0], font_name)

        font = QFont([font_name])
        families = font.families()
        self.assertEqual(len(families), 1)
        self.assertEqual(families[0], font_name)


if __name__ == '__main__':
    unittest.main()
