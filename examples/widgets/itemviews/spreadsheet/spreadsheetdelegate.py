# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import (QAbstractItemModel, QDate, QModelIndex, QObject,
                            QStringListModel, Qt, Slot)
from PySide6.QtWidgets import (QCompleter, QDateTimeEdit, QLineEdit,
                               QStyleOptionViewItem, QStyledItemDelegate, QWidget)


class SpreadSheetDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def create_editor(self, parent: QWidget,
                      option: QStyleOptionViewItem,
                      index: QModelIndex) -> QWidget:
        if index.column() == 1:
            editor = QDateTimeEdit(parent)
            editor.setDisplayFormat("dd/M/yyyy")
            editor.setCalendarPopup(True)
            return editor

        editor = QLineEdit(parent)

        # create a completer with the strings in the column as model
        allStrings = QStringListModel()
        for i in range(1, index.model().rowCount()):
            strItem = str(index.model().data(index.sibling(i, index.column()),
                                             Qt.ItemDataRole.EditRole))

            if not allStrings.contains(strItem):
                allStrings.append(strItem)

        autoComplete = QCompleter(allStrings)
        editor.setCompleter(autoComplete)
        editor.editingFinished.connect(SpreadSheetDelegate.commit_and_close_editor)
        return editor

    @Slot()
    def commit_and_close_editor(self) -> None:
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def set_editor_data(self, editor: QWidget, index: QModelIndex) -> None:
        edit = QLineEdit(editor)
        if edit:
            edit.setText(str(index.model().data(index, Qt.ItemDataRole.EditRole)))
            return

        dateEditor = QDateTimeEdit(editor)
        if dateEditor:
            dateEditor.setDate(
                QDate.fromString(
                    str(index.model().data(index, Qt.ItemDataRole.EditRole)), "d/M/yyyy"))

    def set_model_data(self, editor: QWidget,
                       model: QAbstractItemModel, index: QModelIndex) -> None:
        edit = QLineEdit(editor)
        if edit:
            model.setData(index, edit.text())
            return

        dateEditor = QDateTimeEdit(editor)
        if dateEditor:
            model.setData(index, dateEditor.date().toString("dd/M/yyyy"))
