#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
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

from mimetypemodel import MimeTypeModel
from PySide6.QtCore import (QDir, QFileInfo, QMimeDatabase, QModelIndex, Qt,
                            Slot)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                               QFileDialog, QInputDialog, QMainWindow,
                               QMessageBox, QSplitter, QTextEdit, QTreeView,
                               QWidget)


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.m_find_index: int = 0
        self.m_model = MimeTypeModel(self)
        self.m_tree_view = QTreeView(self)
        self.m_details_text = QTextEdit(self)
        self.m_find_matches = []

        self.setWindowTitle("Qt Mime Database Browser")

        # create actions
        self.detect_file_action = QAction(
            "&Detect File Type...", self, shortcut="Ctrl+O", triggered=self.detect_file
        )
        self.exit_action = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.m_find_action = QAction("&Find...", self, shortcut="Ctrl+F", triggered=self.find)
        self.m_find_next_action = QAction(
            "Find &Next", self, shortcut="Ctrl+G", triggered=self.find_next
        )
        self.m_find_previous_action = QAction(
            "Find &Previous",
            self,
            shortcut="Ctrl+Shift+G",
            triggered=self.find_previous,
        )
        self.about_action = QAction(
            "About Qt",
            self,
            shortcut=QKeySequence(QKeySequence.HelpContents),
            triggered=QApplication.aboutQt,
        )

        # add action to menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.detect_file_action)
        self.file_menu.addAction(self.exit_action)
        self.find_menu = self.menuBar().addMenu("&Edit")
        self.find_menu.addAction(self.m_find_action)
        self.find_menu.addAction(self.m_find_next_action)
        self.find_menu.addAction(self.m_find_previous_action)
        self.about_menu = self.menuBar().addMenu("&About")
        self.about_menu.addAction(self.about_action)

        self.central_splitter = QSplitter(self)
        self.setCentralWidget(self.central_splitter)

        self.m_tree_view.setUniformRowHeights(True)
        self.m_tree_view.setModel(self.m_model)

        self.items = self.m_model.findItems(
            "application/octet-stream",
            Qt.MatchContains | Qt.MatchFixedString | Qt.MatchRecursive,
        )

        if self.items:
            self.m_tree_view.expand(self.m_model.indexFromItem(self.items[0]))

        self.m_tree_view.selectionModel().currentChanged.connect(self.current_changed)
        self.central_splitter.addWidget(self.m_tree_view)
        self.m_details_text.setReadOnly(True)
        self.central_splitter.addWidget(self.m_details_text)

        self.update_find_actions()

    @Slot()
    def detect_file(self):
        file_name = QFileDialog.getOpenFileName(self, "Choose File")
        if not file_name:
            return

        mime_database = QMimeDatabase()
        fi = QFileInfo(file_name[0])
        mime_type = mime_database.mimeTypeForFile(fi)
        index = (
            self.m_model.indexForMimeType(mime_type.name())
            if mime_type.isValid()
            else QModelIndex()
        )

        if index.isValid():
            self.statusBar().showMessage(f'{fi.fileName()}" is of type "{mime_type.name()}"')
            self._select_and_goto(index)
        else:
            QMessageBox.information(
                self,
                "Unknown File Type",
                f"The type of {QDir.toNativeSeparators(file_name)} could not be determined.",
            )

    @Slot()
    def find(self):
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle("Find")
        input_dialog.setLabelText("Text")
        if input_dialog.exec() != QDialog.Accepted:
            return

        value = input_dialog.textValue().strip()
        if not value:
            return

        self.m_find_matches.clear()
        self.m_find_index = 0
        items = self.m_model.findItems(
            value, Qt.MatchContains | Qt.MatchFixedString | Qt.MatchRecursive
        )

        for item in items:
            self.m_find_matches.append(self.m_model.indexFromItem(item))

        self.statusBar().showMessage(f'{len(self.m_find_matches)} mime types match "{value}".')
        self.update_find_actions()

        if self.m_find_matches:
            self._select_and_goto(self.m_find_matches[0])

    @Slot()
    def find_next(self):
        self.m_find_index = self.m_find_index + 1
        if self.m_find_index >= len(self.m_find_matches):
            self.m_find_index = 0
        if self.m_find_index < len(self.m_find_matches):
            self._select_and_goto(self.m_find_matches[self.m_find_index])

    @Slot()
    def find_previous(self):
        self.m_find_index = self.m_find_index - 1
        if self.m_find_index < 0:
            self.m_find_index = len(self.m_find_matches) - 1
        if self.m_find_index >= 0:
            self._select_and_goto(self.m_find_matches[self.m_find_index])

    @Slot(QModelIndex)
    def current_changed(self, index: QModelIndex):
        if index.isValid():
            self.m_details_text.setText(
                MimeTypeModel.formatMimeTypeInfo(self.m_model.mimeType(index))
            )

    def update_find_actions(self):
        self.find_next_previous_enabled = len(self.m_find_matches) > 1
        self.m_find_next_action.setEnabled(self.find_next_previous_enabled)
        self.m_find_previous_action.setEnabled(self.find_next_previous_enabled)

    def _select_and_goto(self, index: QModelIndex):
        self.m_tree_view.scrollTo(index, QAbstractItemView.PositionAtCenter)
        self.m_tree_view.setCurrentIndex(index)
