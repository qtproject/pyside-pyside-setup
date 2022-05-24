# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QCoreApplication, QObject, QTimer


class Dispatcher(QObject):
    _me = None

    def __init__(self):
        super().__init__()
        self._me = self
        QTimer.singleShot(0, self._finish)

    def _finish(self):
        del self._me  # It can't crash here!
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        QTimer.singleShot(10, QCoreApplication.instance().quit)


if __name__ == '__main__':
    app = QCoreApplication([])
    Dispatcher()
    app.exec()
