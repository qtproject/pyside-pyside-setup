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

import sys

from PySide6.QtWidgets import (QAbstractItemView, QApplication, QMainWindow,
                               QListView)
from PySide6.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData,
                            QModelIndex, QStringListModel, Qt)


class DragDropListModel(QStringListModel):
    """A simple model that uses a QStringList as its data source."""

    def __init__(self, strings, parent=None):
          super().__init__(strings, parent)

#! [0]

    def canDropMimeData(self, data, action, row, column, parent):
        if not data.hasFormat("application/vnd.text.list"):
            return False

        if column > 0:
            return False

        return True
#! [0]
#! [1]
    def dropMimeData(self, data, action, row, column, parent):
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if action == Qt.IgnoreAction:
            return True
#! [1]

#! [2]
        begin_row = 0

        if row != -1:
            begin_row = row
#! [2] #! [3]
        elif parent.isValid():
            begin_row = parent.row()
#! [3] #! [4]
        else:
            begin_row = self.rowCount(QModelIndex())
#! [4]

#! [5]
        encoded_data = data.data("application/vnd.text.list")
        stream = QDataStream(encoded_data, QIODevice.ReadOnly)
        new_items = []
        while not stream.atEnd():
            new_items.append(stream.readQString())
#! [5]

#! [6]
        self.insertRows(begin_row, len(new_items), QModelIndex())
        for text in new_items:
            idx = self.index(begin_row, 0, QModelIndex())
            self.setData(idx, text)
            begin_row += 1

        return True
#! [6]

#! [7]
    def flags(self, index):
        default_flags = super().flags(index)
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | default_flags
        return Qt.ItemIsDropEnabled | default_flags
#! [7]

#! [8]
    def mimeData(self, indexes):
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.WriteOnly)
        for index in indexes:
            if index.isValid():
                text = self.data(index, Qt.DisplayRole)
                stream.writeQString(text)

        mime_data.setData("application/vnd.text.list", encoded_data)
        return mime_data
#! [8]

#! [9]
    def mimeTypes(self):
        return ["application/vnd.text.list"]
#! [9]

#! [10]
    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction
#! [10]


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        file_menu = self.menuBar().addMenu("&File")
        quit_action = file_menu.addAction("E&xit")
        quit_action.setShortcut("Ctrl+Q")

#! [mainwindow0]
        self._list_view = QListView(self)
        self._list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._list_view.setDragEnabled(True)
        self._list_view.setAcceptDrops(True)
        self._list_view.setDropIndicatorShown(True)
#! [mainwindow0]

        quit_action.triggered.connect(self.close)

        self.setup_list_items()

        self.setCentralWidget(self._list_view)
        self.setWindowTitle("List View")

    def setup_list_items(self):
        items = ["Oak", "Fir", "Pine", "Birch", "Hazel", "Redwood", "Sycamore",
                 "Chestnut", "Mahogany"]
        model = DragDropListModel(items, self)
        self._list_view.setModel(model)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
