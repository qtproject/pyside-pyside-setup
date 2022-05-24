# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QGraphicsWidget


class TestBug549(unittest.TestCase):
    def testBug(self):
        app = QApplication([])
        w = QGraphicsWidget()
        w.setContentsMargins(1, 2, 3, 4)
        self.assertEqual(w.getContentsMargins(), (1, 2, 3, 4))
        w.setWindowFrameMargins(5, 6, 7, 8)
        self.assertEqual(w.getWindowFrameMargins(), (5, 6, 7, 8))


if __name__ == '__main__':
    unittest.main()

