
#############################################################################
##
## Copyright (C) 2009 Darryl Wallace, 2009 <wallacdj@gmail.com>
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

from PySide6 import QtCore, QtWidgets


class FileListModel(QtCore.QAbstractListModel):
    number_populated = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(FileListModel, self).__init__(parent)

        self._file_count = 0
        self._file_list = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self._file_count

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self._file_list) or index.row() < 0:
            return None

        if role == QtCore.Qt.DisplayRole:
            return self._file_list[index.row()]

        if role == QtCore.Qt.BackgroundRole:
            batch = (index.row() // 100) % 2
#  FIXME: QGuiApplication::palette() required
            if batch == 0:
                return qApp.palette().base()

            return qApp.palette().alternateBase()

        return None

    def canFetchMore(self, index):
        return self._file_count < len(self._file_list)

    def fetchMore(self, index):
        remainder = len(self._file_list) - self._file_count
        items_to_fetch = min(100, remainder)

        self.beginInsertRows(QtCore.QModelIndex(), self._file_count,
                self._file_count + items_to_fetch)

        self._file_count += items_to_fetch

        self.endInsertRows()

        self.number_populated.emit(items_to_fetch)

    def set_dir_path(self, path):
        dir = QtCore.QDir(path)

        self.beginResetModel()
        self._file_list = list(dir.entryList())
        self._file_count = 0
        self.endResetModel()


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        model = FileListModel(self)
        model.set_dir_path(QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.PrefixPath))

        label = QtWidgets.QLabel("Directory")
        line_edit = QtWidgets.QLineEdit()
        label.setBuddy(line_edit)

        view = QtWidgets.QListView()
        view.setModel(model)

        self._log_viewer = QtWidgets.QTextBrowser()
        self._log_viewer.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred))

        line_edit.textChanged.connect(model.set_dir_path)
        line_edit.textChanged.connect(self._log_viewer.clear)
        model.number_populated.connect(self.update_log)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(line_edit, 0, 1)
        layout.addWidget(view, 1, 0, 1, 2)
        layout.addWidget(self._log_viewer, 2, 0, 1, 2)

        self.setLayout(layout)
        self.setWindowTitle("Fetch More Example")

    def update_log(self, number):
        self._log_viewer.append(f"{number} items added.")


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec_())
