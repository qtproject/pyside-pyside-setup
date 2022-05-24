# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from helper.usesqapplication import UsesQApplication


class QListWidgetTest(UsesQApplication):

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def populateList(self, lst):
        o = QObject()
        o.setObjectName("obj")

        item = QListWidgetItem("item0")
        item.setData(Qt.UserRole, o)
        # item._data = o
        self.assertTrue(sys.getrefcount(o), 3)
        self.assertTrue(sys.getrefcount(item), 2)
        lst.addItem(item)
        self.assertTrue(sys.getrefcount(item), 3)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def checkCurrentItem(self, lst):
        item = lst.currentItem()
        self.assertTrue(sys.getrefcount(item), 3)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def checkItemData(self, lst):
        item = lst.currentItem()
        o = item.data(Qt.UserRole)
        self.assertTrue(sys.getrefcount(o), 4)
        self.assertEqual(o, item._data)
        self.assertTrue(sys.getrefcount(o), 2)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testConstructorWithParent(self):
        lst = QListWidget()
        self.populateList(lst)
        self.checkCurrentItem(lst)
        i = lst.item(0)
        self.assertTrue(sys.getrefcount(i), 3)

        del lst
        self.assertTrue(sys.getrefcount(i), 2)
        del i

    def testIt(self):
        lst = QListWidget()
        lst.show()
        slot = lambda: lst.removeItemWidget(lst.currentItem())
        lst.addItem(QListWidgetItem("foo"))
        QTimer.singleShot(0, slot)
        QTimer.singleShot(0, lst.close)
        self.app.exec()
        self.assertEqual(lst.count(), 1)

    def testClear(self):
        lst = QListWidget()
        lst.addItem("foo")
        item = lst.item(0)
        self.assertIsNone(lst.clear())
        self.assertRaises(RuntimeError, lambda: item.text())


if __name__ == '__main__':
    unittest.main()
