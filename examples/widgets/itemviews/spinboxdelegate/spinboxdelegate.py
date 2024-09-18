# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtWidgets import (QApplication, QStyledItemDelegate, QSpinBox,
                               QTableView)
from PySide6.QtGui import QStandardItemModel, Qt
from PySide6.QtCore import QModelIndex

"""PySide6 port of the widgets/itemviews/spinboxdelegate from Qt v6.x"""


#! [0]
class SpinBoxDelegate(QStyledItemDelegate):
    """A delegate that allows the user to change integer values from the model
       using a spin box widget. """

#! [0]
    def __init__(self, parent=None):
        super().__init__(parent)
#! [0]

#! [1]
    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor
#! [1]

#! [2]
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setValue(value)
#! [2]

#! [3]
    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.ItemDataRole.EditRole)
#! [3]

#! [4]
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
#! [4]


#! [main0]
if __name__ == '__main__':
    app = QApplication(sys.argv)

    model = QStandardItemModel(4, 2)
    tableView = QTableView()
    tableView.setModel(model)

    delegate = SpinBoxDelegate()
    tableView.setItemDelegate(delegate)
#! [main0]

    tableView.horizontalHeader().setStretchLastSection(True)

#! [main1]
    for row in range(4):
        for column in range(2):
            index = model.index(row, column, QModelIndex())
            value = (row + 1) * (column + 1)
            model.setData(index, value)
#! [main1] //# [main2]
#! [main2]

#! [main3]
    tableView.setWindowTitle("Spin Box Delegate")
    tableView.show()
    sys.exit(app.exec())
#! [main3]
