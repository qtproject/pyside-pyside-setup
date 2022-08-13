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
from itertools import chain

from PySide6.QtCore import QAbstractTableModel, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView

"""PySide6 port of the widgets/tutorials/modelview/5_edit example from Qt v6.x"""


COLS = 3
ROWS = 2


class MyModel(QAbstractTableModel):

    editCompleted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid_data = [["" for y in range(COLS)] for x in range(ROWS)]

    def rowCount(self, parent=None):
        return ROWS

    def columnCount(self, parent=None):
        return COLS

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and self.checkIndex(index):
            return self._grid_data[index.row()][index.column()]
        return None

#! [1]
    def setData(self, index, value, role):
        if role != Qt.EditRole or not self.checkIndex(index):
            return False
        # save value from editor to member m_gridData
        self._grid_data[index.row()][index.column()] = value
        # for presentation purposes only: build and emit a joined string
        result = " ".join(chain(*self._grid_data))
        self.editCompleted.emit(result)
        return True
#! [1]

#! [2]
    def flags(self, index):
        return Qt.ItemIsEditable | super().flags(index)
#! [2]


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_view = QTableView(self)
        self.setCentralWidget(self._table_view)
        my_model = MyModel(self)
        self._table_view.setModel(my_model)
        # transfer changes to the model to the window title
        my_model.editCompleted.connect(self.show_window_title)

    @Slot(str)
    def show_window_title(self, title):
        self.setWindowTitle(title)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
