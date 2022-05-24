# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QTableView, QVBoxLayout, QApplication
from PySide6.QtCore import QAbstractItemModel

from helper.usesqapplication import UsesQApplication


class VirtualList(QAbstractItemModel):
    def __getitem__(self, index):
        self._getItemCalled = True
        pass

    def rowCount(self, parent):
        return 5000

    def columnCount(self, parent):
        return 3

    def index(self, row, column, parent):
        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()

    def data(self, index, role):
        row = index.row()
        col = index.column()
        return f"({row}, {col})"


class TestQAbstractItemModel(UsesQApplication):
    def testSetModel(self):
        model = VirtualList()
        model._getItemCalled = False
        table = QTableView()
        table.setModel(model)
        table.show()
        self.assertFalse(model._getItemCalled)


if __name__ == "__main__":
    unittest.main()

