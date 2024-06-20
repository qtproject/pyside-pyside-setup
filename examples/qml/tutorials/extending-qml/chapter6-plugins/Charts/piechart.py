# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Property
from PySide6.QtQml import QmlElement, ListProperty
from PySide6.QtQuick import QQuickItem

from pieslice import PieSlice

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Charts"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PieChart(QQuickItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._slices = []
        self._name = ''

    @Property(str, final=True)
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def slice(self, n):
        return self._slices[n]

    def sliceCount(self):
        return len(self._slices)

    def append_and_setparent(self, slice):
        self._slices.append(slice)
        slice.setParentItem(self)

    slices = ListProperty(PieSlice, append_and_setparent)
