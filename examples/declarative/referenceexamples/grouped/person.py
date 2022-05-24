# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QObject, Property
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlAnonymous, QmlElement

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "examples.grouped.people"
QML_IMPORT_MAJOR_VERSION = 1


@QmlAnonymous
class ShoeDescription(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._brand = ''
        self._size = 0
        self._price = 0
        self._color = QColor()

    @Property(str)
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, b):
        self._brand = b

    @Property(int)
    def size(self):
        return self._size

    @size.setter
    def size(self, s):
        self._size = s

    @Property(float)
    def price(self):
        return self._price

    @price.setter
    def price(self, p):
        self._price = p

    @Property(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        self._color = c


@QmlAnonymous
class Person(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = ''
        self._shoe = ShoeDescription()

    @Property(str)
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @Property(ShoeDescription)
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
