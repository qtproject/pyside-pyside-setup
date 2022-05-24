# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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


class TestQModelIndexInternalPointer(unittest.TestCase):

    def testInternalPointer(self):
        m = MyModel()
        foo = QObject()
        idx = m.createIndex(0, 0, foo)
        check = m.checkIndex(idx, QAbstractItemModel.CheckIndexOption.IndexIsValid
                                  | QAbstractItemModel.CheckIndexOption.DoNotUseParent
                                  | QAbstractItemModel.CheckIndexOption.ParentIsInvalid)
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


if __name__ == '__main__':
    unittest.main()

