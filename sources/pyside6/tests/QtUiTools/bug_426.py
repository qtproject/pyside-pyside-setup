# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader


class Window(object):
    def __init__(self):
        loader = QUiLoader()
        filePath = os.path.join(os.path.dirname(__file__), 'bug_426.ui')
        self.widget = loader.load(filePath)
        self.group = QActionGroup(self.widget)
        self.widget.show()
        QTimer.singleShot(0, self.widget.close)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec())
