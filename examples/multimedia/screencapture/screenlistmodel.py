# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QAbstractListModel, Qt, Slot


class ScreenListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        app = qApp  # noqa: F821
        app.screenAdded.connect(self.screens_changed)
        app.screenRemoved.connect(self.screens_changed)
        app.primaryScreenChanged.connect(self.screens_changed)

    def rowCount(self, index):
        return len(QGuiApplication.screens())

    def data(self, index, role):
        screen_list = QGuiApplication.screens()

        if role == Qt.ItemDataRole.DisplayRole:
            screen = screen_list[index.row()]
            w = screen.size().width()
            h = screen.size().height()
            dpi = screen.logicalDotsPerInch()
            return f'"{screen.name()}" {w}x{h}, {dpi}DPI'

        return None

    def screen(self, index):
        return QGuiApplication.screens()[index.row()]

    @Slot()
    def screens_changed(self):
        self.beginResetModel()
        self.endResetModel()
