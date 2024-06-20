# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class VariantBarDataMapping(QObject):

    rowIndexChanged = Signal()
    columnIndexChanged = Signal()
    valueIndexChanged = Signal()
    rowCategoriesChanged = Signal()
    columnCategoriesChanged = Signal()
    mappingChanged = Signal()

    def __init__(self, rowIndex, columnIndex, valueIndex,
                 rowCategories=[], columnCategories=[]):
        super().__init__(None)
        self._rowIndex = rowIndex
        self._columnIndex = columnIndex
        self._valueIndex = valueIndex
        self._rowCategories = rowCategories
        self._columnCategories = columnCategories

    def setRowIndex(self, index):
        self._rowIndex = index
        self.mappingChanged.emit()

    def rowIndex(self):
        return self._rowIndex

    def setColumnIndex(self, index):
        self._columnIndex = index
        self.mappingChanged.emit()

    def columnIndex(self):
        return self._columnIndex

    def setValueIndex(self, index):
        self._valueIndex = index
        self.mappingChanged.emit()

    def valueIndex(self):
        return self._valueIndex

    def setRowCategories(self, categories):
        self._rowCategories = categories
        self.mappingChanged.emit()

    def rowCategories(self):
        return self._rowCategories

    def setColumnCategories(self, categories):
        self._columnCategories = categories
        self.mappingChanged.emit()

    def columnCategories(self):
        return self._columnCategories

    def remap(self, rowIndex, columnIndex, valueIndex,
              rowCategories=[], columnCategories=[]):
        self._rowIndex = rowIndex
        self._columnIndex = columnIndex
        self._valueIndex = valueIndex
        self._rowCategories = rowCategories
        self._columnCategories = columnCategories
        self.mappingChanged.emit()
