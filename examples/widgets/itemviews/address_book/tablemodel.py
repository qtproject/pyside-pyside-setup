# Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import (Qt, QAbstractTableModel, QModelIndex)


class TableModel(QAbstractTableModel):

    def __init__(self, addresses=None, parent=None):
        super().__init__(parent)
        self.addresses = addresses if addresses is not None else []

    def rowCount(self, index=QModelIndex()):
        """ Returns the number of rows the model holds. """
        return len(self.addresses)

    def columnCount(self, index=QModelIndex()):
        """ Returns the number of columns the model holds. """
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of Qt's
            "invalid QVariant").
        """
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            if 0 <= row < len(self.addresses):
                match index.column():
                    case 0:
                        return self.addresses[row]["name"]
                    case 1:
                        return self.addresses[row]["address"]
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """ Set the headers to be displayed. """
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            match section:
                case 0:
                    return "Name"
                case 1:
                    return "Address"
        return None

    def insertRows(self, position, rows=1, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.addresses.insert(position + row, {"name": "", "address": ""})

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.addresses[position:position + rows]

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """ Adjust the data (set it to <value>) depending on the given
            index and role.
        """
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        if 0 <= row < len(self.addresses):
            address = self.addresses[row]
            match index.column():
                case 0:
                    address["name"] = value
                case 1:
                    address["address"] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole.value])
            return True

        return False

    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)
                            | Qt.ItemFlag.ItemIsEditable)
