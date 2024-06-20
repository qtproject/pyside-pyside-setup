# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtGraphs import QBarDataProxy, QBarDataItem


class VariantBarDataProxy(QBarDataProxy):

    def __init__(self):
        super().__init__()
        self._dataSet = None
        self._mapping = None

    def setDataSet(self, newSet):
        if self._dataSet:
            self._dataSet.itemsAdded.disconnect(self.handleItemsAdded)
            self._dataSet.dataCleared.disconnect(self.handleDataCleared)

        self._dataSet = newSet

        if self._dataSet:
            self._dataSet.itemsAdded.connect(self.handleItemsAdded)
            self._dataSet.dataCleared.connect(self.handleDataCleared)
        self.resolveDataSet()

    def dataSet(self):
        return self._dataSet.data()

    # Map key (row, column, value) to value index in data item (VariantItem).
    # Doesn't gain ownership of mapping, but does connect to it to listen for
    # mapping changes. Modifying mapping that is set to proxy will trigger
    # dataset re-resolving.
    def setMapping(self, mapping):
        if self._mapping:
            self._mapping.mappingChanged.disconnect(self.handleMappingChanged)

        self._mapping = mapping

        if self._mapping:
            self._mapping.mappingChanged.connect(self.handleMappingChanged)

        self.resolveDataSet()

    def mapping(self):
        return self._mapping.data()

    @Slot(int, int)
    def handleItemsAdded(self, index, count):
        # Resolve new items
        self.resolveDataSet()

    @Slot()
    def handleDataCleared(self):
        # Data cleared, reset array
        self.resetArray(None)

    @Slot()
    def handleMappingChanged(self):
        self.resolveDataSet()

    # Resolve entire dataset into QBarDataArray.
    def resolveDataSet(self):
        # If we have no data or mapping, or the categories are not defined,
        # simply clear the array
        if (not self._dataSet or not self._mapping
                or not self._mapping.rowCategories()
                or not self._mapping.columnCategories()):
            self.resetArray()
            return

        itemList = self._dataSet.itemList()

        rowIndex = self._mapping.rowIndex()
        columnIndex = self._mapping.columnIndex()
        valueIndex = self._mapping.valueIndex()
        rowList = self._mapping.rowCategories()
        columnList = self._mapping.columnCategories()

        # Sort values into rows and columns
        itemValueMap = {}
        for item in itemList:
            key = str(item[rowIndex])
            v = itemValueMap.get(key)
            if not v:
                v = {}
                itemValueMap[key] = v
            v[str(item[columnIndex])] = float(item[valueIndex])

        # Create a new data array in format the parent class understands
        newProxyArray = []
        for rowKey in rowList:
            newProxyRow = []
            for i in range(0, len(columnList)):
                item = QBarDataItem(itemValueMap[rowKey][columnList[i]])
                newProxyRow.append(item)
            newProxyArray.append(newProxyRow)

        # Finally, reset the data array in the parent class
        self.resetArray(newProxyArray)
