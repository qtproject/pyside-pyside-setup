# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QAbstractListModel, QModelIndex, QTimer
from PySide6.QtWidgets import QApplication, QListView


class ListModel(QAbstractListModel):
    def rowCount(self, parent=QModelIndex()):
        return 0


if __name__ == '__main__':
    app = QApplication([])
    model = ListModel()
    v = QListView()
    v.setModel(model)
    v.show()
    QTimer.singleShot(0, v.close)
    app.exec()
