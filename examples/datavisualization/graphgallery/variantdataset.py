# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class VariantDataSet(QObject):

    itemsAdded = Signal(int, int)
    dataCleared = Signal()

    def __init__(self):
        super().__init__()
        self._variantData = []

    def clear(self):
        for item in self._variantData:
            item.clear()
            del item

        self._variantData.clear()
        self.dataCleared.emit()

    def addItem(self, item):
        self._variantData.append(item)
        addIndex = len(self._variantData)

        self.itemsAdded.emit(addIndex, 1)
        return addIndex

    def addItems(self, itemList):
        newCount = len(itemList)
        addIndex = len(self._variantData)
        self._variantData.extend(itemList)
        self.itemsAdded.emit(addIndex, newCount)
        return addIndex

    def itemList(self):
        return self._variantData
