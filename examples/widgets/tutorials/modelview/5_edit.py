# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

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

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and self.checkIndex(index):
            return self._grid_data[index.row()][index.column()]
        return None

#! [1]
    def setData(self, index, value, role):
        if role != Qt.ItemDataRole.EditRole or not self.checkIndex(index):
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
