# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import sys
import os
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtWidgets import (QApplication, QCommonStyle, QPushButton)


text = ''


class Style(QCommonStyle):

    def drawControl(self, element, option, painter, widget=None):
        # This should be a QStyleOptionButton with a "text" field
        global text
        text = option.text


class StyleOptionTest(UsesQApplication):
    '''PYSIDE-1909: Test cast to derived style option classes.'''

    def testStyle(self):
        global text
        button = QPushButton("Hello World")
        button.setStyle(Style())
        button.show()
        while not text:
            QApplication.processEvents()
        self.assertEqual(text, button.text())


if __name__ == '__main__':
    unittest.main()
