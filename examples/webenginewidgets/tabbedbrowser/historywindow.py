# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtWidgets import QApplication, QTreeView

from PySide6.QtCore import Signal, QAbstractTableModel, QModelIndex, Qt, QUrl


class HistoryModel(QAbstractTableModel):

    def __init__(self, history, parent=None):
        super().__init__(parent)
        self._history = history

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return 'Title' if section == 0 else 'Url'
        return None

    def rowCount(self, index=QModelIndex()):
        return self._history.count()

    def columnCount(self, index=QModelIndex()):
        return 2

    def item_at(self, model_index):
        return self._history.itemAt(model_index.row())

    def data(self, index, role=Qt.DisplayRole):
        item = self.item_at(index)
        column = index.column()
        if role == Qt.DisplayRole:
            return item.title() if column == 0 else item.url().toString()
        return None

    def refresh(self):
        self.beginResetModel()
        self.endResetModel()


class HistoryWindow(QTreeView):

    open_url = Signal(QUrl)

    def __init__(self, history, parent):
        super().__init__(parent)

        self._model = HistoryModel(history, self)
        self.setModel(self._model)
        self.activated.connect(self._activated)

        screen = QApplication.desktop().screenGeometry(parent)
        self.resize(screen.width() / 3, screen.height() / 3)
        self._adjustSize()

    def refresh(self):
        self._model.refresh()
        self._adjustSize()

    def _adjustSize(self):
        if (self._model.rowCount() > 0):
            self.resizeColumnToContents(0)

    def _activated(self, index):
        item = self._model.item_at(index)
        self.open_url.emit(item.url())
