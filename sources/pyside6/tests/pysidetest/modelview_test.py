#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import TestView
from PySide6.QtCore import QAbstractListModel, QObject, QModelIndex

'''Tests model/view relationship.'''

object_name = 'test object'


class MyObject(QObject):
    pass


class ListModelKeepsReference(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.obj = MyObject()
        self.obj.setObjectName(object_name)

    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role):
        return self.obj


class ListModelDoesntKeepsReference(QAbstractListModel):
    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role):
        obj = MyObject()
        obj.setObjectName(object_name)
        return obj


class ListModelThatReturnsString(QAbstractListModel):
    def rowCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role):
        self.obj = 'string'
        return self.obj


class ModelViewTest(unittest.TestCase):

    def testListModelDoesntKeepsReference(self):
        model = ListModelDoesntKeepsReference()
        view = TestView(model)
        obj = view.getData()
        self.assertEqual(type(obj), MyObject)
        self.assertEqual(obj.objectName(), object_name)
        obj.metaObject()

    def testListModelKeepsReference(self):
        model = ListModelKeepsReference()
        view = TestView(model)
        obj = view.getData()
        self.assertEqual(type(obj), MyObject)
        self.assertEqual(obj.objectName(), object_name)

    def testListModelThatReturnsString(self):
        model = ListModelThatReturnsString()
        view = TestView(model)
        obj = view.getData()
        self.assertEqual(type(obj), str)
        self.assertEqual(obj, 'string')


if __name__ == '__main__':
    unittest.main()

