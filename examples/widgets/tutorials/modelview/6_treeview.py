# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView

"""PySide6 port of the widgets/tutorials/modelview/6_treeview example from Qt v6.x"""


#! [1]
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._standard_model = QStandardItemModel(self)
        self._tree_view = QTreeView(self)
        self.setCentralWidget(self._tree_view)

        prepared_row = self.prepare_row("first", "second", "third")
        item = self._standard_model.invisibleRootItem()
        # adding a row to the invisible root item produces a root element
        item.appendRow(prepared_row)

        second_row = self.prepare_row("111", "222", "333")
        # adding a row to an item starts a subtree
        prepared_row[0].appendRow(second_row)

        self._tree_view.setModel(self._standard_model)
        self._tree_view.expandAll()

    def prepare_row(self, first, second, third):
        return [QStandardItem(first), QStandardItem(second),
                QStandardItem(third)]
#! [1]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
