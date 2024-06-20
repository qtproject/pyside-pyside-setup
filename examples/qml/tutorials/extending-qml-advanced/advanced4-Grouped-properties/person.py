# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlAnonymous, QmlElement

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "People"
QML_IMPORT_MAJOR_VERSION = 1


@QmlAnonymous
class ShoeDescription(QObject):
    brand_changed = Signal()
    size_changed = Signal()
    price_changed = Signal()
    color_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._brand = ''
        self._size = 0
        self._price = 0
        self._color = QColor()

    @Property(str, notify=brand_changed, final=True)
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, b):
        if self._brand != b:
            self._brand = b
            self.brand_changed.emit()

    @Property(int, notify=size_changed, final=True)
    def size(self):
        return self._size

    @size.setter
    def size(self, s):
        if self._size != s:
            self._size = s
            self.size_changed.emit()

    @Property(float, notify=price_changed, final=True)
    def price(self):
        return self._price

    @price.setter
    def price(self, p):
        if self._price != p:
            self._price = p
            self.price_changed.emit()

    @Property(QColor, notify=color_changed, final=True)
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        if self._color != c:
            self._color = c
            self.color_changed.emit()


@QmlAnonymous
class Person(QObject):
    name_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = ''
        self._shoe = ShoeDescription()

    @Property(str, notify=name_changed, final=True)
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        if self._name != n:
            self._name = n
            self.name_changed.emit()

    @Property(ShoeDescription, final=True)
    def shoe(self):
        return self._shoe


@QmlElement
class Boy(Person):
    def __init__(self, parent=None):
        super().__init__(parent)


@QmlElement
class Girl(Person):
    def __init__(self, parent=None):
        super().__init__(parent)
