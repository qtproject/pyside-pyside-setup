# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations


from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlElement

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "BaseModel"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class BaseModel(QAbstractListModel):

    RatioRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.db = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.db)

    def roleNames(self):
        default = super().roleNames()
        default[self.RatioRole] = QByteArray(b"ratio")
        default[Qt.ItemDataRole.BackgroundRole] = QByteArray(b"backgroundColor")
        return default

    def data(self, index, role: int):
        if not self.db:
            ret = None
        elif not index.isValid():
            ret = None
        elif role == Qt.ItemDataRole.DisplayRole:
            ret = self.db[index.row()]["text"]
        elif role == Qt.ItemDataRole.BackgroundRole:
            ret = self.db[index.row()]["bgColor"]
        elif role == self.RatioRole:
            ret = self.db[index.row()]["ratio"]
        else:
            ret = None
        return ret

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.ItemDataRole.EditRole:
            self.db[index.row()]["text"] = value
        return True

    @Slot(result=bool)
    def append(self):
        """Slot to append a row at the end"""
        return self.insertRow(self.rowCount())

    def insertRow(self, row):
        """Insert a single row at row"""
        return self.insertRows(row, 0)

    def insertRows(self, row: int, count, index=QModelIndex()):
        """Insert n rows (n = 1 + count)  at row"""

        self.beginInsertRows(QModelIndex(), row, row + count)

        # start database work
        if len(self.db):
            newid = max(x["id"] for x in self.db) + 1
        else:
            newid = 1
        for i in range(count + 1):  # at least one row
            self.db.insert(
                row, {"id": newid, "text": "new", "bgColor": QColor("purple"), "ratio": 0.2}
            )
        # end database work
        self.endInsertRows()
        return True

    @Slot(int, int, result=bool)
    def move(self, source: int, target: int):
        """Slot to move a single row from source to target"""
        return self.moveRow(QModelIndex(), source, QModelIndex(), target)

    def moveRow(self, sourceParent, sourceRow, dstParent, dstChild):
        """Move a single row"""
        return self.moveRows(sourceParent, sourceRow, 0, dstParent, dstChild)

    def moveRows(self, sourceParent, sourceRow, count, dstParent, dstChild):
        """Move n rows (n=1+ count)  from sourceRow to dstChild"""

        if sourceRow == dstChild:
            return False

        elif sourceRow > dstChild:
            end = dstChild

        else:
            end = dstChild + 1

        self.beginMoveRows(QModelIndex(), sourceRow, sourceRow + count, QModelIndex(), end)

        # start database work
        pops = self.db[sourceRow: sourceRow + count + 1]
        if sourceRow > dstChild:
            self.db = (
                self.db[:dstChild]
                + pops
                + self.db[dstChild:sourceRow]
                + self.db[sourceRow + count + 1:]
            )
        else:
            start = self.db[:sourceRow]
            middle = self.db[dstChild: dstChild + 1]
            endlist = self.db[dstChild + count + 1:]
            self.db = start + middle + pops + endlist
        # end database work

        self.endMoveRows()
        return True

    @Slot(int, result=bool)
    def remove(self, row: int):
        """Slot to remove one row"""
        return self.removeRow(row)

    def removeRow(self, row, parent=QModelIndex()):
        """Remove one row at index row"""
        return self.removeRows(row, 0, parent)

    def removeRows(self, row: int, count: int, parent=QModelIndex()):
        """Remove n rows (n=1+count) starting at row"""
        self.beginRemoveRows(QModelIndex(), row, row + count)

        # start database work
        self.db = self.db[:row] + self.db[row + count + 1:]
        # end database work

        self.endRemoveRows()
        return True

    @Slot(result=bool)
    def reset(self):
        self.beginResetModel()
        self.resetInternalData()  # should work without calling it ?
        self.endResetModel()
        return True

    def resetInternalData(self):
        self.db = [
            {"id": 3, "bgColor": QColor("red"), "ratio": 0.15, "text": "first"},
            {"id": 1, "bgColor": QColor("blue"), "ratio": 0.1, "text": "second"},
            {"id": 2, "bgColor": QColor("green"), "ratio": 0.2, "text": "third"},
        ]
