
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2016 The Qt Company Ltd.
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

"""PySide6 port of the widgets/dialogs/findfiles example from Qt v5.x"""

import sys

from PySide6.QtCore import (QCoreApplication, QDir, QFile, QFileInfo,
                            QIODevice, QTextStream, QUrl, Qt)
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                               QDialog, QFileDialog, QGridLayout, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QProgressDialog,
                               QPushButton, QSizePolicy, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)


class Window(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._browse_button = self.create_button("&Browse...", self.browse)
        self._find_button = self.create_button("&Find", self.find)

        self._file_combo_box = self.create_combo_box("*")
        self._text_combo_box = self.create_combo_box()
        self._directory_combo_box = self.create_combo_box(QDir.currentPath())

        file_label = QLabel("Named:")
        text_label = QLabel("Containing text:")
        directory_label = QLabel("In directory:")
        self._files_found_label = QLabel()

        self.create_files_table()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._find_button)

        main_layout = QGridLayout()
        main_layout.addWidget(file_label, 0, 0)
        main_layout.addWidget(self._file_combo_box, 0, 1, 1, 2)
        main_layout.addWidget(text_label, 1, 0)
        main_layout.addWidget(self._text_combo_box, 1, 1, 1, 2)
        main_layout.addWidget(directory_label, 2, 0)
        main_layout.addWidget(self._directory_combo_box, 2, 1)
        main_layout.addWidget(self._browse_button, 2, 2)
        main_layout.addWidget(self._files_table, 3, 0, 1, 3)
        main_layout.addWidget(self._files_found_label, 4, 0)
        main_layout.addLayout(buttons_layout, 5, 0, 1, 3)
        self.setLayout(main_layout)

        self.setWindowTitle("Find Files")
        self.resize(500, 300)

    def browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Find Files",
                QDir.currentPath())

        if directory:
            if self._directory_combo_box.findText(directory) == -1:
                self._directory_combo_box.addItem(directory)

            self._directory_combo_box.setCurrentIndex(self._directory_combo_box.findText(directory))

    @staticmethod
    def update_combo_box(comboBox):
        if comboBox.findText(comboBox.currentText()) == -1:
            comboBox.addItem(comboBox.currentText())

    def find(self):
        self._files_table.setRowCount(0)

        file_name = self._file_combo_box.currentText()
        text = self._text_combo_box.currentText()
        path = self._directory_combo_box.currentText()

        self.update_combo_box(self._file_combo_box)
        self.update_combo_box(self._text_combo_box)
        self.update_combo_box(self._directory_combo_box)

        self._current_dir = QDir(path)
        if not file_name:
            file_name = "*"
        files = self._current_dir.entryList([file_name],
                QDir.Files | QDir.NoSymLinks)

        if text:
            files = self.find_files(files, text)
        self.show_files(files)

    def find_files(self, files, text):
        progress_dialog = QProgressDialog(self)

        progress_dialog.setCancelButtonText("&Cancel")
        progress_dialog.setRange(0, len(files))
        progress_dialog.setWindowTitle("Find Files")

        found_files = []

        for i in range(len(files)):
            progress_dialog.setValue(i)
            n = len(files)
            progress_dialog.setLabelText(f"Searching file number {i} of {n}...")
            QCoreApplication.processEvents()

            if progress_dialog.wasCanceled():
                break

            in_file = QFile(self._current_dir.absoluteFilePath(files[i]))

            if in_file.open(QIODevice.ReadOnly):
                stream = QTextStream(in_file)
                while not stream.atEnd():
                    if progress_dialog.wasCanceled():
                        break
                    line = stream.readLine()
                    if text in line:
                        found_files.append(files[i])
                        break

        progress_dialog.close()

        return found_files

    def show_files(self, files):
        for fn in files:
            file = QFile(self._current_dir.absoluteFilePath(fn))
            size = QFileInfo(file).size()

            file_name_item = QTableWidgetItem(fn)
            file_name_item.setFlags(file_name_item.flags() ^ Qt.ItemIsEditable)
            size_kb = int((size + 1023) / 1024)
            size_item = QTableWidgetItem(f"{size_kb} KB")
            size_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            size_item.setFlags(size_item.flags() ^ Qt.ItemIsEditable)

            row = self._files_table.rowCount()
            self._files_table.insertRow(row)
            self._files_table.setItem(row, 0, file_name_item)
            self._files_table.setItem(row, 1, size_item)

        n = len(files)
        self._files_found_label.setText(f"{n} file(s) found (Double click on a file to open it)")

    def create_button(self, text, member):
        button = QPushButton(text)
        button.clicked.connect(member)
        return button

    def create_combo_box(self, text=""):
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.addItem(text)
        combo_box.setSizePolicy(QSizePolicy.Expanding,
                QSizePolicy.Preferred)
        return combo_box

    def create_files_table(self):
        self._files_table = QTableWidget(0, 2)
        self._files_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self._files_table.setHorizontalHeaderLabels(("File Name", "Size"))
        self._files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._files_table.verticalHeader().hide()
        self._files_table.setShowGrid(False)

        self._files_table.cellActivated.connect(self.open_file_of_item)

    def open_file_of_item(self, row, column):
        item = self._files_table.item(row, 0)

        QDesktopServices.openUrl(QUrl(self._current_dir.absoluteFilePath(item.text())))


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
