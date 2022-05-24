# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QAbstractListModel, QCoreApplication, QModelIndex


class MyModel (QAbstractListModel):
    def rowCount(self, parent=None):
        return 3


class TestBug706(unittest.TestCase):

    def mySlot(self, idx, start, end):
        self.start = start
        self.end = end

    def testIt(self):
        self.start = None
        self.end = None

        app = QCoreApplication([])
        model = MyModel()
        model.columnsAboutToBeInserted.connect(self.mySlot)
        model.columnsAboutToBeInserted.emit(QModelIndex(), 0, 1)
        self.assertEqual(self.start, 0)
        self.assertEqual(self.end, 1)


if __name__ == '__main__':
    unittest.main()
