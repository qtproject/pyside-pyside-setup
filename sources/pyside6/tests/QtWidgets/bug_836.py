# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QFrame


class Mixin1(object):
    pass


class Mixin2(object):
    pass


class Mixin3(object):
    pass


class MainWindow(Mixin1, Mixin2, Mixin3, QFrame):
    def __init__(self):
        super().__init__()


def main():
    app = QApplication([])
    # if it doesn't crash it should pass
    w = MainWindow()
    w.show()
    QTimer.singleShot(0, w.close)
    app.exec()


if __name__ == "__main__":
    main()


