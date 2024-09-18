# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMenu, QTableView

from receivedframesmodel import clipboard_text_role


class ReceivedFramesView(QTableView):

    def __init__(self, parent):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

    @Slot(QPoint)
    def _context_menu(self, pos):
        context_menu = QMenu("Context menu", self)
        if self.selectedIndexes():
            copy_action = QAction("Copy", self)
            copy_action.triggered.connect(self.copy_row)
            context_menu.addAction(copy_action)

        select_all_action = QAction("Select all", self)
        select_all_action.triggered.connect(self.selectAll)
        context_menu.addAction(select_all_action)
        context_menu.exec(self.mapToGlobal(pos))

    def set_model(self, model):
        super().setModel(model)
        for i in range(0, model.columnCount()):
            size = model.headerData(i, Qt.Orientation.Horizontal, Qt.ItemDataRole.SizeHintRole)
            self.setColumnWidth(i, size.width())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_row()
        elif event.matches(QKeySequence.SelectAll):
            self.selectAll()
        else:
            super().keyPressEvent(event)

    @Slot()
    def copy_row(self):
        clipboard = QApplication.clipboard()
        str_row = ""
        last_column = self.model().columnCount() - 1
        for index in self.selectedIndexes():
            str_row += index.data(clipboard_text_role) + " "
            if index.column() == last_column:
                str_row += "\n"
        clipboard.setText(str_row)
