# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from PySide6.QtGui import QStandardItemModel, QStandardItem
from shiboken6 import Shiboken
from helper.usesqapplication import UsesQApplication


class QStandardItemModelTest(UsesQApplication):

    def setUp(self):
        super(QStandardItemModelTest, self).setUp()
        self.parent = QObject()
        self.model = QStandardItemModel(0, 3, self.parent)

    def tearDown(self):
        del self.parent
        del self.model
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(QStandardItemModelTest, self).tearDown()

    def testInsertRow(self):
        # bug #227
        self.model.insertRow(0)

    def testClear(self):

        model = QStandardItemModel()
        root = model.invisibleRootItem()
        model.clear()
        self.assertFalse(Shiboken.isValid(root))


class QStandardItemModelRef(UsesQApplication):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefCount(self):
        model = QStandardItemModel(5, 5)
        items = []
        for r in range(5):
            row = []
            for c in range(5):
                row.append(QStandardItem(f"{r},{c}"))
                self.assertEqual(sys.getrefcount(row[c]), 2)

            model.insertRow(r, row)

            for c in range(5):
                ref_after = sys.getrefcount(row[c])
                # check if the ref count was incremented after insertRow
                self.assertEqual(ref_after, 3)

            items.append(row)
            row = None

        for r in range(3):
            my_row = model.takeRow(0)
            my_row = None
            for c in range(5):
                # only rest 1 reference
                self.assertEqual(sys.getrefcount(items[r][c]), 2)

        my_i = model.item(0, 0)
        # ref(my_i) + parent_ref + items list ref
        self.assertEqual(sys.getrefcount(my_i), 4)

        model.clear()
        # ref(my_i)
        self.assertEqual(sys.getrefcount(my_i), 3)


if __name__ == '__main__':
    unittest.main()

