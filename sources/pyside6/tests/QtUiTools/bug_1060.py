# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' unit test for BUG #1060 '''

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader


class MyQUiLoader(QUiLoader):
    def __init__(self):
        super().__init__()

    def createWidget(self, *args):
        return super(MyQUiLoader, self).createWidget(*args)


if __name__ == "__main__":
    app = QApplication([])

    file = Path(__file__).resolve().parent / 'bug_1060.ui'
    assert(file.is_file())
    ui = MyQUiLoader().load(file)
    ui.show()
