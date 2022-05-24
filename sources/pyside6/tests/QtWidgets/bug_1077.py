# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' unit test for BUG #1077 '''

import os
import sys
import time

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtGui import QSyntaxHighlighter
from PySide6.QtWidgets import QApplication, QTextEdit, QWidget


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent, mode):
        super().__init__(parent)
        self.tstamp = time.time()


if __name__ == "__main__":
    app = QApplication([])
    python = QTextEdit()
    python.setWindowTitle("python")
    hl = Highlighter(python.document(), "python")
    python.show()
    text = hl.document()
