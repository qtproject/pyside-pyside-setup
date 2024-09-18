# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import json

from PySide6.QtWidgets import (QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMenu, QTreeView)
from PySide6.QtGui import (QAction, QIcon, QKeySequence,
                           QPixmap, QTextDocument)
from PySide6.QtCore import (QAbstractItemModel, QDir,
                            QIODevice, QModelIndex,
                            QPoint, QSize, Qt, Slot)

from abstractviewer import AbstractViewer


def resizeToContents(tree):
    for i in range(0, tree.header().count()):
        tree.resizeColumnToContents(i)


class JsonTreeItem:

    def __init__(self, parent=None):
        self._key = ""
        self._value = None
        self._children = []
        self._parent = parent

    def key(self):
        return self._key

    def value(self):
        return self._value

    def appendChild(self, item):
        self._children.append(item)

    def child(self, row):
        return self._children[row]

    def parent(self):
        return self._parent

    def childCount(self):
        return len(self._children)

    def row(self):
        if self._parent:
            return self._parent._children.index(self)
        return 0

    def setKey(self, key):
        self._key = key

    def setValue(self, value):
        self._value = value

    @staticmethod
    def load(value, parent=None):
        rootItem = JsonTreeItem(parent)
        rootItem.setKey("root")

        if isinstance(value, dict):
            for key, val in value.items():
                child = JsonTreeItem.load(val, rootItem)
                child.setKey(key)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, val in enumerate(value):
                child = JsonTreeItem.load(val, rootItem)
                child.setKey(f"{index}")
                rootItem.appendChild(child)

        else:
            rootItem.setValue(value)

        return rootItem


class JsonItemModel(QAbstractItemModel):

    def columnCount(self, index=QModelIndex()):
        return 2

    def itemFromIndex(self, index):
        return index.internalPointer()

    def __init__(self, doc, parent):
        super().__init__(parent)
        self._textItem = JsonTreeItem()

        # Append header lines
        self._headers = ["Key", "Value"]

        # Reset the model. Root can either be a value or an array.
        self.beginResetModel()
        self._textItem = JsonTreeItem.load(doc) if doc else JsonTreeItem()
        self.endResetModel()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self.itemFromIndex(index)
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.key()
            if index.column() == 1:
                return item.value()
        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return item.value()
        return None

    def headerData(self, section, orientation, role):
        return (self._headers[section]
                if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal
                else None)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return None

        parentItem = JsonTreeItem()

        if not parent.isValid():
            parentItem = self._textItem
        else:
            parentItem = self.itemFromIndex(parent)

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return None

    def parent(self, index):
        if not index.isValid():
            return None

        childItem = self.itemFromIndex(index)
        parentItem = childItem.parent()

        if parentItem == self._textItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        parentItem = JsonTreeItem()
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._textItem
        else:
            parentItem = self.itemFromIndex(parent)
        return parentItem.childCount()


class JsonViewer(AbstractViewer):

    def __init__(self):
        super().__init__()
        self._tree = QTreeView()
        self._toplevel = None
        self._text = ""
        self._searchKey = None
        self.uiInitialized.connect(self.setupJsonUi)

    def init(self, file, parent, mainWindow):
        self._tree = QTreeView(parent)
        super().init(file, self._tree, mainWindow)

    def viewerName(self):
        return "JsonViewer"

    def supportedMimeTypes(self):
        return ["application/json"]

    @Slot()
    def setupJsonUi(self):
        # Build Menus and toolbars
        menu = self.addMenu("Json")
        tb = self.addToolBar("Json Actions")

        zoomInIcon = QIcon.fromTheme(QIcon.ThemeIcon.ZoomIn)
        a = menu.addAction(zoomInIcon, "&+Expand all", self._tree.expandAll)
        tb.addAction(a)
        a.setPriority(QAction.LowPriority)
        a.setShortcut(QKeySequence.New)

        zoomOutIcon = QIcon.fromTheme(QIcon.ThemeIcon.ZoomOut)
        a = menu.addAction(zoomOutIcon, "&-Collapse all", self._tree.collapseAll)
        tb.addAction(a)
        a.setPriority(QAction.LowPriority)
        a.setShortcut(QKeySequence.New)

        if not self._searchKey:
            self._searchKey = QLineEdit(tb)

        label = QLabel(tb)
        magnifier = QPixmap(":/icons/images/magnifier.png").scaled(QSize(28, 28))
        label.setPixmap(magnifier)
        tb.addWidget(label)
        tb.addWidget(self._searchKey)
        self._searchKey.textEdited.connect(self._tree.keyboardSearch)

        if not self.openJsonFile():
            return

        # Populate bookmarks with toplevel
        self._uiAssets_tabs.clear()
        self._toplevel = QListWidget(self._uiAssets_tabs)
        self._uiAssets_tabs.addTab(self._toplevel, "Bookmarks")
        for i in range(0, self._tree.model().rowCount()):
            index = self._tree.model().index(i, 0)
            self._toplevel.addItem(index.data())
            item = self._toplevel.item(i)
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip(f"Toplevel Item {i}")

        self._toplevel.setAcceptDrops(True)
        self._tree.setDragEnabled(True)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._toplevel.setContextMenuPolicy(Qt.CustomContextMenu)

        self._toplevel.itemClicked.connect(self.onTopLevelItemClicked)
        self._toplevel.itemDoubleClicked.connect(self.onTopLevelItemDoubleClicked)
        self._toplevel.customContextMenuRequested.connect(self.onBookmarkMenuRequested)
        self._tree.customContextMenuRequested.connect(self.onJsonMenuRequested)

        # Connect back and forward
        self._uiAssets_back.triggered.connect(self._back)
        self._uiAssets_forward.triggered.connect(self._forward)

    @Slot()
    def _back(self):
        index = self._tree.indexAbove(self._tree.currentIndex())
        if index.isValid():
            self._tree.setCurrentIndex(index)

    @Slot()
    def _forward(self):
        current = self._tree.currentIndex()
        next = self._tree.indexBelow(current)
        if next.isValid():
            self._tree.setCurrentIndex(next)
            return
        # Expand last item to go beyond
        if not self._tree.isExpanded(current):
            self._tree.expand(current)
            next = self._tree.indexBelow(current)
            if next.isValid():
                self._tree.setCurrentIndex(next)

    def openJsonFile(self):
        self.disablePrinting()
        file_name = QDir.toNativeSeparators(self._file.fileName())
        type = "open"
        self._file.open(QIODevice.ReadOnly)
        self._text = self._file.readAll().data().decode("utf-8")
        self._file.close()

        data = None
        message = None
        try:
            data = json.loads(self._text)
            message = f"Json document {file_name} opened"
            model = JsonItemModel(data, self)
            self._tree.setModel(model)
        except ValueError as e:
            message = f"Unable to parse Json document from {file_name}: {e}"
        self.statusMessage(message, type)
        self.maybeEnablePrinting()

        return self._tree.model() is not None

    def indexOf(self, item):
        return QModelIndex(item.data(Qt.ItemDataRole.UserRole))

    @Slot(QListWidgetItem)
    def onTopLevelItemClicked(self, item):
        """Move to the clicked toplevel index"""
        # return in the unlikely case that the tree has not been built
        if not self._tree.model():
            return

        index = self.indexOf(item)
        if not index.isValid():
            return

        self._tree.setCurrentIndex(index)

    @Slot(QListWidgetItem)
    def onTopLevelItemDoubleClicked(self, item):
        """Toggle double clicked index between collaps/expand"""

        # return in the unlikely case that the tree has not been built
        if not self._tree.model():
            return

        index = self.indexOf(item)
        if not index.isValid():
            return

        if self._tree.isExpanded(index):
            self._tree.collapse(index)
            return

        # Make sure the node and all parents are expanded
        while index.isValid():
            self._tree.expand(index)
            index = index.parent()

    @Slot(QPoint)
    def onJsonMenuRequested(self, pos):
        index = self._tree.indexAt(pos)
        if not index.isValid():
            return

        # Don't show a context menu, if the index is already a bookmark
        for i in range(0, self._toplevel.count()):
            if self.indexOf(self._toplevel.item(i)) == index:
                return

        menu = QMenu(self._tree)
        action = QAction("Add bookmark")
        action.setData(index)
        menu.addAction(action)
        action.triggered.connect(self.onBookmarkAdded)
        menu.exec(self._tree.mapToGlobal(pos))

    @Slot(QPoint)
    def onBookmarkMenuRequested(self, pos):
        item = self._toplevel.itemAt(pos)
        if not item:
            return

        # Don't delete toplevel items
        index = self.indexOf(item)
        if not index.parent().isValid():
            return

        menu = QMenu()
        action = QAction("Delete bookmark")
        action.setData(self._toplevel.row(item))
        menu.addAction(action)
        action.triggered.connect(self.onBookmarkDeleted)
        menu.exec(self._toplevel.mapToGlobal(pos))

    @Slot()
    def onBookmarkAdded(self):
        action = self.sender()
        if not action:
            return

        index = action.data()
        if not index.isValid():
            return

        item = QListWidgetItem(index.data(Qt.ItemDataRole.DisplayRole), self._toplevel)
        item.setData(Qt.ItemDataRole.UserRole, index)

        # Set a tooltip that shows where the item is located in the tree
        parent = index.parent()
        tooltip = index.data(Qt.ItemDataRole.DisplayRole).toString()
        while parent.isValid():
            tooltip = parent.data(Qt.ItemDataRole.DisplayRole).toString() + "." + tooltip
            parent = parent.parent()

        item.setToolTip(tooltip)

    @Slot()
    def onBookmarkDeleted(self):
        action = self.sender()
        if not action:
            return

        row = action.data().toInt()
        if row < 0 or row >= self._toplevel.count():
            return

        self._toplevel.takeItem(row)

    def hasContent(self):
        return bool(self._text)

    def supportsOverview(self):
        return True

    def printDocument(self, printer):
        if not self.hasContent():
            return
        doc = QTextDocument(self._text)
        doc.print_(printer)
