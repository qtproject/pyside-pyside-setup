#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for objects that keep references to other object without owning them (e.g. model/view relationships).'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import ObjectModel, ObjectType, ObjectView


object_name = 'test object'

class MyObject(ObjectType):
    pass

class ListModelKeepsReference(ObjectModel):
    def __init__(self, parent=None):
        ObjectModel.__init__(self, parent)
        self.obj = MyObject()
        self.obj.setObjectName(object_name)

    def data(self):
        return self.obj

class ListModelDoesntKeepsReference(ObjectModel):
    def data(self):
        obj = MyObject()
        obj.setObjectName(object_name)
        return obj


class ModelViewTest(unittest.TestCase):

    def testListModelDoesntKeepsReference(self):
        model = ListModelDoesntKeepsReference()
        view = ObjectView(model)
        obj = view.getRawModelData()
        self.assertEqual(type(obj), MyObject)
        self.assertEqual(obj.objectName(), object_name)

    def testListModelKeepsReference(self):
        model = ListModelKeepsReference()
        view = ObjectView(model)
        obj = view.getRawModelData()
        self.assertEqual(type(obj), MyObject)
        self.assertEqual(obj.objectName(), object_name)


if __name__ == '__main__':
    unittest.main()

