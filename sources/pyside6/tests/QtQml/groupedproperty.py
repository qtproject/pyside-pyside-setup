# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""Test grouped properties (PYSIDE-1836)."""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import (QCoreApplication, QUrl, QObject, Property)
from PySide6.QtQml import (QQmlComponent, QQmlEngine, QmlAnonymous, QmlElement)


QML_IMPORT_NAME = "grouped"
QML_IMPORT_MAJOR_VERSION = 1


@QmlAnonymous
class ShoeDescription(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._brand = ""
        self._size = 0
        self._price = 0

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

    @Property(int)
    def price(self):
        return self._price

    @price.setter
    def price(self, p):
        self._price = p


@QmlElement
class Person(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = ""
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


def component_error(component):
    result = ""
    for e in component.errors():
        if result:
            result += "\n"
        result += str(e)
    return result


class TestQmlGroupedProperties(unittest.TestCase):
    def testIt(self):
        app = QCoreApplication(sys.argv)
        file = Path(__file__).resolve().parent / "groupedproperty.qml"
        url = QUrl.fromLocalFile(file)
        engine = QQmlEngine()
        component = QQmlComponent(engine, url)
        person = component.create()
        self.assertTrue(person, component_error(component))

        # Check the meta type of the property
        meta_object = person.metaObject()
        index = meta_object.indexOfProperty("shoe")
        self.assertTrue(index > 0)
        meta_property = meta_object.property(index)
        meta_type = meta_property.metaType()
        self.assertTrue(meta_type.isValid())

        # Check the values
        self.assertEqual(person.shoe.brand, "Bikey")
        self.assertEqual(person.shoe.price, 90)
        self.assertEqual(person.shoe.size, 12)

        del engine


if __name__ == '__main__':
    unittest.main()
