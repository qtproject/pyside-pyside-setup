# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QItemSelection, Qt, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView

"""PySide6 port of the widgets/tutorials/modelview/7_selections example from Qt v6.x"""


#! [1]
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._standard_model = QStandardItemModel(self)
        self._tree_view = QTreeView(self)
        self.setCentralWidget(self._tree_view)

        # defining a couple of items
        root_node = self._standard_model.invisibleRootItem()

        america_item = QStandardItem("America")
        mexico_item = QStandardItem("Canada")
        usa_item = QStandardItem("USA")
        boston_item = QStandardItem("Boston")
        europe_item = QStandardItem("Europe")
        italy_item = QStandardItem("Italy")
        rome_item = QStandardItem("Rome")
        verona_item = QStandardItem("Verona")

        # building up the hierarchy
        root_node.appendRow(america_item)
        root_node.appendRow(europe_item)
        america_item.appendRow(mexico_item)
        america_item.appendRow(usa_item)
        usa_item.appendRow(boston_item)
        europe_item.appendRow(italy_item)
        italy_item.appendRow(rome_item)
        italy_item.appendRow(verona_item)

        self._tree_view.setModel(self._standard_model)
        self._tree_view.expandAll()

        # selection changes shall trigger a slot
        selection_model = self._tree_view.selectionModel()
        selection_model.selectionChanged.connect(self.selection_changed_slot)
#! [1]

#! [2]
    @Slot(QItemSelection, QItemSelection)
    def selection_changed_slot(self, new_selection, old_selection):
        # get the text of the selected item
        index = self._tree_view.selectionModel().currentIndex()
        selected_text = index.data(Qt.ItemDataRole.DisplayRole)
        # find out the hierarchy level of the selected item
        hierarchy_level = 1
        seek_root = index
        while seek_root.parent().isValid():
            seek_root = seek_root.parent()
            hierarchy_level += 1
        self.setWindowTitle(f"{selected_text}, Level {hierarchy_level}")
#! [2]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
