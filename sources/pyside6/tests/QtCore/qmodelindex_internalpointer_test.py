# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test case for QAbstractListModel.createIndex and QModelIndex.internalPointer'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QAbstractListModel, QObject


class MyModel (QAbstractListModel):
    pass


class TestQModelIndexInternalPointer(unittest.TestCase):
    ''' Test case for QAbstractListModel.createIndex and QModelIndex.internalPointer'''

    def setUp(self):
        # Acquire resources
        self.model = MyModel()

    def tearDown(self):
        # Release resources
        del self.model
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testInternalPointer(self):
        # Test QAbstractListModel.createIndex and
        # QModelIndex.internalPointer with regular Python objects
        obj = QObject()
        idx = self.model.createIndex(0, 0, "Hello")
        i = idx.internalPointer()
        self.assertEqual(i, "Hello")

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReferenceCounting(self):
        # Test reference counting when retrieving data with
        # QModelIndex.internalPointer
        o = [1, 2, 3]
        o_refcnt = sys.getrefcount(o)
        idx = self.model.createIndex(0, 0, o)
        ptr = idx.internalPointer()
        self.assertEqual(sys.getrefcount(o), o_refcnt + 1)

    def testIndexForDefaultDataArg(self):
        # Test QAbstractListModel.createIndex with a default
        # value for data argument
        idx = self.model.createIndex(0, 0)
        self.assertEqual(None, idx.internalPointer())


if __name__ == '__main__':
    unittest.main()

