#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
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

import json
import sys
from typing import Any, Iterable, List, Dict, Union

from PySide6.QtWidgets import QTreeView, QApplication, QHeaderView
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, QFileInfo


class TreeItem:
    """A Json item corresponding to a line in QTreeView"""

    def __init__(self, parent: "TreeItem" = None):
        self._parent = parent
        self._key = ""
        self._value = ""
        self._value_type = None
        self._children = []

    def appendChild(self, item: "TreeItem"):
        """Add item as a child"""
        self._children.append(item)

    def child(self, row: int) -> "TreeItem":
        """Return the child of the current item from the given row"""
        return self._children[row]

    def parent(self) -> "TreeItem":
        """Return the parent of the current item"""
        return self._parent

    def childCount(self) -> int:
        """Return the number of children of the current item"""
        return len(self._children)

    def row(self) -> int:
        """Return the row where the current item occupies in the parent"""
        return self._parent._children.index(self) if self._parent else 0

    @property
    def key(self) -> str:
        """Return the key name"""
        return self._key

    @key.setter
    def key(self, key: str):
        """Set key name of the current item"""
        self._key = key

    @property
    def value(self) -> str:
        """Return the value name of the current item"""
        return self._value

    @value.setter
    def value(self, value: str):
        """Set value name of the current item"""
        self._value = value

    @property
    def value_type(self):
        """Return the python type of the item's value."""
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        """Set the python type of the item's value."""
        self._value_type = value

    @classmethod
    def load(
        cls, value: Union[List, Dict], parent: "TreeItem" = None, sort=True
    ) -> "TreeItem":
        """Create a 'root' TreeItem from a nested list or a nested dictonary

        Examples:
            with open("file.json") as file:
                data = json.dump(file)
                root = TreeItem.load(data)

        This method is a recursive function that calls itself.

        Returns:
            TreeItem: TreeItem
        """
        rootItem = TreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = sorted(value.items()) if sort else value.items()

            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.value_type = type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = index
                child.value_type = type(value)
                rootItem.appendChild(child)

        else:
            rootItem.value = value
            rootItem.value_type = type(value)

        return rootItem


class JsonModel(QAbstractItemModel):
    """ An editable model of Json data """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._rootItem = TreeItem()
        self._headers = ("key", "value")

    def clear(self):
        """ Clear data from the model """
        self.load({})

    def load(self, document: dict):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(
            document, (dict, list, tuple)
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()

        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)

        self.endResetModel()

        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.key

            if index.column() == 1:
                return item.value

        elif role == Qt.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if role == Qt.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                item.value = str(value)

                if __binding__ in ("PySide", "PyQt4"):
                    self.dataChanged.emit(index, index)
                else:
                    self.dataChanged.emit(index, index, [Qt.EditRole])

                return True

        return False

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override from QAbstractItemModel

        For the JsonModel, it returns only data for columns (orientation = Horizontal)

        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent

        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index

        """

        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(JsonModel, self).flags(index)

        if index.column() == 1:
            return Qt.ItemIsEditable | flags
        else:
            return flags

    def to_json(self, item=None):

        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.value_type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_json(ch)
            return document

        elif item.value_type == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_json(ch))
            return document

        else:
            return item.value


if __name__ == "__main__":

    app = QApplication(sys.argv)
    view = QTreeView()
    model = JsonModel()

    view.setModel(model)

    json_path = QFileInfo(__file__).absoluteDir().filePath("example.json")

    with open(json_path) as file:
        document = json.load(file)
        model.load(document)

    view.show()
    view.header().setSectionResizeMode(0, QHeaderView.Stretch)
    view.setAlternatingRowColors(True)
    view.resize(500, 300)
    app.exec()
