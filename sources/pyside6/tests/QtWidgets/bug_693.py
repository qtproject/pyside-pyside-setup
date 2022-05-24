# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QAbstractListModel, QLine
from PySide6.QtWidgets import QApplication, QListView


class MyModel (QAbstractListModel):

    stupidLine = QLine(0, 0, 10, 10)

    def rowCount(self, parent):
        return 1

    def data(self, index, role):
        return self.stupidLine


class TestBug693(unittest.TestCase):
    def testIt(self):
        app = QApplication([])
        model = MyModel()
        view = QListView()
        view.setModel(model)
        view.show()

        # This must NOT throw the exception:
        # RuntimeError: Internal C++ object (PySide6.QtCore.QLine) already deleted.
        MyModel.stupidLine.isNull()


if __name__ == "__main__":
    unittest.main()
