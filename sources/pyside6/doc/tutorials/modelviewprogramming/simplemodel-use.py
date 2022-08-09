# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtWidgets import (QApplication, QFileSystemModel, QLabel,
                               QVBoxLayout, QWidget)
from PySide6.QtGui import QPalette
from PySide6.QtCore import QDir, Qt


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    layout = QVBoxLayout(window)
    title = QLabel("Some items from the directory model", window)
    title.setBackgroundRole(QPalette.Base)
    title.setMargin(8)
    layout.addWidget(title)

#! [0]
    model = QFileSystemModel()
    model.setRootPath(QDir.currentPath())

    def on_directory_loaded(directory):
        parent_index = model.index(directory)
        num_rows = model.rowCount(parent_index)
#! [1]
        for row in range(num_rows):
            index = model.index(row, 0, parent_index)
#! [1]
#! [2]
            text = model.data(index, Qt.DisplayRole)
#! [2]
            label = QLabel(text, window)
            layout.addWidget(label)

    model.directoryLoaded.connect(on_directory_loaded)
#! [0]

    window.setWindowTitle("A simple model example")
    window.show()
    sys.exit(app.exec())
