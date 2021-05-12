
#############################################################################
##
## Copyright (C) 2009 Darryl Wallace, 2009 <wallacdj@gmail.com>
## Copyright (C) 2013 Riverbank Computing Limited.
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

"""PySide6 port of the itemviews/fetchmore/fetchmore example from Qt v6.x

Navigate to a directory with many entries by doubleclicking and scroll
down the list to see the model being populated on demand.
"""

import sys

from PySide6.QtCore import (QAbstractListModel, QDir, QFileInfo, QLibraryInfo,
                            QModelIndex, Qt, Signal, Slot)
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (QApplication, QFileIconProvider, QListView,
                               QPlainTextEdit, QSizePolicy, QVBoxLayout,
                               QWidget)


BATCH_SIZE = 100


class FileListModel(QAbstractListModel):

    number_populated = Signal(str, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._path = ''
        self._file_count = 0
        self._file_list = []
        self._icon_provider = QFileIconProvider()

    def rowCount(self, parent=QModelIndex()):
        return self._file_count

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        if row >= len(self._file_list) or row < 0:
            return None

        if role == Qt.DisplayRole:
            return self._file_list[row].fileName()

        if role == Qt.BackgroundRole:
            batch = row // BATCH_SIZE
            palette = qApp.palette()
            return palette.base() if batch % 2 == 0 else palette.alternateBase()

        if role == Qt.DecorationRole:
            return self._icon_provider.icon(self._file_list[row])

        return None

    def canFetchMore(self, index):
        return self._file_count < len(self._file_list)

    def fetchMore(self, index):
        start = self._file_count
        total = len(self._file_list)
        remainder = total - start
        items_to_fetch = min(BATCH_SIZE, remainder)

        self.beginInsertRows(QModelIndex(), start, start + items_to_fetch)

        self._file_count += items_to_fetch

        self.endInsertRows()

        self.number_populated.emit(self._path, start, items_to_fetch, total)

    @Slot(str)
    def set_dir_path(self, path):
        self._path = path
        directory = QDir(path)

        self.beginResetModel()
        directory_filter = QDir.AllEntries | QDir.NoDot
        self._file_list = directory.entryInfoList(directory_filter, QDir.Name)
        self._file_count = 0
        self.endResetModel()

    def fileinfo_at(self, index):
        return self._file_list[index.row()]


class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._model = FileListModel(self)
        self._model.set_dir_path(QDir.rootPath())

        self._view = QListView()
        self._view.setModel(self._model)

        self._log_viewer = QPlainTextEdit()
        self._log_viewer.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
                                       QSizePolicy.Preferred))

        self._model.number_populated.connect(self.update_log)
        self._view.activated.connect(self.activated)

        layout = QVBoxLayout(self)
        layout.addWidget(self._view)
        layout.addWidget(self._log_viewer)

        self.setWindowTitle("Fetch More Example")

    @Slot(str, int, int)
    def update_log(self, path, start, number, total):
        native_path = QDir.toNativeSeparators(path)
        last = start + number - 1
        entry = f'{start}..{last}/{total} items from "{native_path}" added.'
        self._log_viewer.appendPlainText(entry)

    @Slot(QModelIndex)
    def activated(self, index):
        fileinfo = self._model.fileinfo_at(index)
        if fileinfo.isDir():
            self._log_viewer.clear()
            self._model.set_dir_path(fileinfo.absoluteFilePath())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    window.resize(400, 500)
    window.show()

    sys.exit(app.exec())
