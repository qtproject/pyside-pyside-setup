# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QItemSelection
from PySide6.QtGui import QStandardItemModel


class QItemSelectionTest(UsesQApplication):
    def testLen(self):
        model = QStandardItemModel(2, 2)
        model.insertRow(0)
        model.insertRow(1)
        model.insertColumn(0)
        model.insertColumn(1)
        selection = QItemSelection(model.index(0, 0), model.index(1, 1))
        self.assertEqual(len(selection), 1)


if __name__ == '__main__':
    unittest.main()

