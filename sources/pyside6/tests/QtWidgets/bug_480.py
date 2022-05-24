# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QVBoxLayout,
                               QWidget)


class BuggyWidget(QWidget):
    def setup(self):
        self.verticalLayout = QVBoxLayout(self)
        self.gridLayout = QGridLayout()
        self.lbl = QLabel(self)
        self.gridLayout.addWidget(self.lbl, 0, 1, 1, 1)

        # this cause a segfault during the ownership transfer
        self.verticalLayout.addLayout(self.gridLayout)


class LayoutTransferOwnerShip(unittest.TestCase):
    def testBug(self):
        app = QApplication([])
        w = BuggyWidget()
        w.setup()
        w.show()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()

