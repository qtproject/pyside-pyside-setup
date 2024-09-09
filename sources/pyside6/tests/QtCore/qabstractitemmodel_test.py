# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import (QAbstractItemModel, QAbstractListModel,
                            QIdentityProxyModel, QObject, QPersistentModelIndex,
                            QStringListModel, Qt)


class MyModel (QAbstractListModel):
    pass


class MyMultiDataModel(QAbstractListModel):

    def multiData(self, index, roleSpans):
        if index.isValid():
            for rd in roleSpans:
                if rd.role() == Qt.ItemDataRole.DisplayRole:
                    rd.setData(f"test {index.row()} {index.column()}")


class TestQModelIndexInternalPointer(unittest.TestCase):

    def testInternalPointer(self):
        m = MyModel()
        foo = QObject()
        idx = m.createIndex(0, 0, foo)
        flags = (QAbstractItemModel.CheckIndexOption.IndexIsValid
                 | QAbstractItemModel.CheckIndexOption.DoNotUseParent
                 | QAbstractItemModel.CheckIndexOption.ParentIsInvalid)
        check = m.checkIndex(idx, flags)
        self.assertTrue(check)

    def testPassQPersistentModelIndexAsQModelIndex(self):
        # Related to bug #716
        m = MyModel()
        idx = QPersistentModelIndex()
        m.span(idx)

    def testQIdentityProxyModel(self):
        sourceModel = QStringListModel(['item1', 'item2'])
        sourceIndex = sourceModel.index(0, 0)
        sourceData = str(sourceModel.data(sourceIndex, Qt.DisplayRole))
        proxyModel = QIdentityProxyModel()
        proxyModel.setSourceModel(sourceModel)
        proxyIndex = proxyModel.mapFromSource(sourceIndex)
        proxyData = str(proxyModel.data(proxyIndex, Qt.DisplayRole))
        self.assertEqual(sourceData, proxyData)

    def testMultiDataModel(self):
        """Test whether QAbstractItemModel.multiData() can be implemented
           using QModelRoleData/QModelRoleDataSpan (ATM syntax only)."""
        model = MyMultiDataModel()  # noqa: F841


if __name__ == '__main__':
    unittest.main()
