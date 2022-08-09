# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtWidgets import (QApplication, QListView)
from PySide6.QtCore import QAbstractListModel, QStringListModel, QModelIndex, Qt


#! [0]
class StringListModel(QAbstractListModel):
    def __init__(self, strings, parent=None):
        super().__init__(parent)
        self._strings = strings

#! [0]
    def rowCount(self, parent=QModelIndex()):
        """Returns the number of items in the string list as the number of rows
           in the model."""
        return len(self._strings)
#! [0]

#! [1]
    def data(self, index, role):
        """Returns an appropriate value for the requested data.
           If the view requests an invalid index, an invalid variant is returned.
           Any valid index that corresponds to a string in the list causes that
          string to be returned."""
        row = index.row()
        if not index.isValid() or row >= len(self._strings):
            return None
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None
        return self._strings[row]
#! [1]

#! [2]
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Returns the appropriate header string depending on the orientation of
           the header and the section. If anything other than the display role is
           requested, we return an invalid variant."""
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return f"Column {section}"
        return f"Row {section}"
#! [2]

#! [3]
    def flags(self, index):
        """Returns an appropriate value for the item's flags. Valid items are
           enabled, selectable, and editable."""

        if not index.isValid():
            return Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsEditable
#! [3]

    #! [4]
    def setData(self, index, value, role=Qt.EditRole):
        """Changes an item in the string list, but only if the following conditions
           are met:

           # The index supplied is valid.
           # The index corresponds to an item to be shown in a view.
           # The role associated with editing text is specified.

           The dataChanged() signal is emitted if the item is changed."""

        if index.isValid() and role == Qt.EditRole:
            self._strings[index.row()] = value
            self.dataChanged.emit(index, index, {role})
            return True
#! [4] #! [5]
        return False
#! [5]

#! [6]
    def insertRows(self, position, rows, parent):
        """Inserts a number of rows into the model at the specified position."""
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self._strings.insert(position, "")
        self.endInsertRows()
        return True
#! [6] #! [7]
#! [7]

#! [8]
    def removeRows(self, position, rows, parent):
        """Removes a number of rows from the model at the specified position."""
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            del self._strings[position]
        self.endRemoveRows()
        return True
#! [8] #! [9]
#! [9]


#! [main0]
if __name__ == '__main__':
    app = QApplication(sys.argv)

#! [main1]
    numbers = ["One", "Two", "Three", "Four", "Five"]
    model = StringListModel(numbers)
#! [main0] #! [main1] #! [main2] #! [main3]
    view = QListView()
#! [main2]
    view.setWindowTitle("View onto a string list model")
#! [main4]
    view.setModel(model)
#! [main3] #! [main4]

    model.insertRows(5, 7, QModelIndex())
    for row in range(5, 12):
        index = model.index(row, 0, QModelIndex())
        model.setData(index, f"{row+1}")

#! [main5]
    view.show()
    sys.exit(app.exec())
#! [main5]
