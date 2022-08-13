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
        selected_text = index.data(Qt.DisplayRole)
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
