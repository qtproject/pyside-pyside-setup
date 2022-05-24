# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListView


class TestBug964 (unittest.TestCase):

    def testIt(self):
        app = QApplication([])
        model = QStringListModel(["1", "2"])
        view = QListView()
        view.setModel(model)
        view.setCurrentIndex(model.index(0, 0))
        newCursor = view.moveCursor(QAbstractItemView.MoveDown, Qt.NoModifier)
        self.assertEqual(newCursor.row(), 1)
        self.assertEqual(newCursor.column(), 0)


if __name__ == "__main__":
    unittest.main()
