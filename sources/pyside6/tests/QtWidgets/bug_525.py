# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMenu


class M2(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("M2"))


class TestMenuDerivedClass(unittest.TestCase):
    def aboutToShowHandler(self):
        pass

    def testConnectSignal(self):
        app = QApplication([])
        m2 = M2()
        # Test if the aboutToShow signal was translated to correct type
        m2.aboutToShow.connect(self.aboutToShowHandler)


if __name__ == '__main__':
    unittest.main()
