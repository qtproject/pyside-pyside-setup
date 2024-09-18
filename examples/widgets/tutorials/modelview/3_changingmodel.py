# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QAbstractTableModel, QTime, QTimer, Qt, Slot
from PySide6.QtWidgets import QApplication, QTableView

"""PySide6 port of the widgets/tutorials/modelview/3_changingmodel example from Qt v6.x"""


class MyModel(QAbstractTableModel):
#! [1]
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.timer_hit)
        self._timer.start()
#! [1]

    def rowCount(self, parent=None):
        return 2

    def columnCount(self, parent=None):
        return 3

#! [2]
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        row = index.row()
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole and row == 0 and col == 0:
            return QTime.currentTime().toString()
        return None
#! [2]

#! [3]
    @Slot()
    def timer_hit(self):
        # we identify the top left cell
        top_left = self.createIndex(0, 0)
        # emit a signal to make the view reread identified data
        self.dataChanged.emit(top_left, top_left, [Qt.ItemDataRole.DisplayRole])
#! [3]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    table_view = QTableView()
    my_model = MyModel()
    table_view.setModel(my_model)
    table_view.show()
    sys.exit(app.exec())
