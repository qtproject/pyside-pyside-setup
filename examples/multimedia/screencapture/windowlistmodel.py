# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, Qt, Slot
from PySide6.QtMultimedia import QWindowCapture


class WindowListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._window_list = QWindowCapture.capturableWindows()

    def rowCount(self, QModelIndex):
        return len(self._window_list)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            window = self._window_list[index.row()]
            return window.description()
        return None

    def window(self, index):
        return self._window_list[index.row()]

    @Slot()
    def populate(self):
        self.beginResetModel()
        self._window_list = QWindowCapture.capturableWindows()
        self.endResetModel()
