# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "People"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Person(QObject):
    name_changed = Signal()
    shoe_size_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = ''
        self._shoe_size = 0

    @Property(str, notify=name_changed, final=True)
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        if self._name != n:
            self._name = n
            self.name_changed.emit()

    @Property(int, notify=shoe_size_changed, final=True)
    def shoe_size(self):
        return self._shoe_size

    @shoe_size.setter
    def shoe_size(self, s):
        if self._shoe_size != s:
            self._shoe_size = s
            self.shoe_size_changed.emit()
