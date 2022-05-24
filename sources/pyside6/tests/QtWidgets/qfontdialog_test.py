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
from PySide6.QtWidgets import QFontDialog
from helper.timedqapplication import TimedQApplication


class TestFontDialog(TimedQApplication):

    def testGetFont(self):
        QFontDialog.getFont()

    def testGetFontQDialog(self):
        QFontDialog.getFont(QFont("FreeSans", 10))

    def testGetFontQDialogQString(self):
        QFontDialog.getFont(QFont("FreeSans", 10), None, "Select font")


if __name__ == '__main__':
    unittest.main()
