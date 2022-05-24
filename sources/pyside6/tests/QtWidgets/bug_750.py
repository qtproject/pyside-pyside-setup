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

from PySide6.QtCore import QTimer
from PySide6.QtGui import QPainter, QFont, QFontInfo
from PySide6.QtWidgets import QWidget


class MyWidget(QWidget):
    def paintEvent(self, e):
        p = QPainter(self)
        self._info = p.fontInfo()
        self._app.quit()


class TestQPainter(UsesQApplication):
    def testFontInfo(self):
        w = MyWidget()
        w._app = self.app
        w._info = None
        QTimer.singleShot(300, w.show)
        self.app.exec()
        self.assertTrue(w._info)


if __name__ == '__main__':
    unittest.main()
