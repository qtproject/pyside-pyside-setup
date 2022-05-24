# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QFrame, QWidget
from PySide6.QtUiTools import QUiLoader


class View_1(QWidget):

    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        file = Path(__file__).resolve().parent / 'bug_552.ui'
        assert(file.is_file())
        widget = loader.load(os.fspath(file), self)
        self.children = []
        for child in widget.findChildren(QObject, None):
            self.children.append(child)
        self.t = widget.tabWidget
        self.t.removeTab(0)


app = QApplication([])
window = View_1()
window.show()

# If it doesn't crash it works :-)
