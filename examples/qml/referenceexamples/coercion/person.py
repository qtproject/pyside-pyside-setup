# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QObject, Property
from PySide6.QtQml import QmlElement, QmlUncreatable

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "examples.coercion.people"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlUncreatable("Person is an abstract base class.")
class Person(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = ''
        self._shoe_size = 0

    @Property(str)
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @Property(int)
    def shoe_size(self):
        return self._shoe_size

    @shoe_size.setter
    def shoe_size(self, s):
        self._shoe_size = s


@QmlElement
class Boy(Person):
    def __init__(self, parent=None):
        super().__init__(parent)


@QmlElement
class Girl(Person):
    def __init__(self, parent=None):
        super().__init__(parent)
