#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

from PySide6.QtCore import (QAbstractItemModel, QDate, QModelIndex, QObject,
                            QStringListModel, Qt, Slot)
from PySide6.QtWidgets import (QCompleter, QDateTimeEdit, QLineEdit,
                               QStyleOptionViewItem, QStyledItemDelegate, QWidget)

from typing import Optional


class SpreadSheetDelegate(QStyledItemDelegate):
    def __init__(self, parent: Optional[QObject] = None) -> None:
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
            strItem = str(index.model().data(index.sibling(i, index.column()), Qt.EditRole))

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
            edit.setText(str(index.model().data(index, Qt.EditRole)))
            return

        dateEditor = QDateTimeEdit(editor)
        if dateEditor:
            dateEditor.setDate(
                QDate.fromString(
                    str(index.model().data(index, Qt.EditRole)), "d/M/yyyy"))

    def set_model_data(self, editor: QWidget,
                       model: QAbstractItemModel, index: QModelIndex) -> None:
        edit = QLineEdit(editor)
        if edit:
            model.setData(index, edit.text())
            return

        dateEditor = QDateTimeEdit(editor)
        if dateEditor:
            model.setData(index, dateEditor.date().toString("dd/M/yyyy"))
