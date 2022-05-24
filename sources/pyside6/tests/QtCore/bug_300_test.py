# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QModelIndex, QStringListModel


class TestQAbstractItemModelSignals(unittest.TestCase):
    def sigCallback(self, index, r, c):
        self._called = True

    def testSignals(self):
        self._called = False
        m = QStringListModel()
        m.rowsAboutToBeInserted[QModelIndex, int, int].connect(self.sigCallback)
        m.insertRows(0, 3)
        self.assertTrue(self._called)


if __name__ == '__main__':
    unittest.main()
