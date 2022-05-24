# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 338: http://bugs.openbossa.org/show_bug.cgi?id=338'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QGraphicsPolygonItem, QGraphicsScene


class DiagramItem(QGraphicsPolygonItem):
    def __init__(self, parent=None, scene=None):
        super().__init__(parent, scene)

    def itemChange(self, change, value):
        return value


class BugTest(unittest.TestCase):
    def test(self):
        app = QApplication(sys.argv)
        scene = QGraphicsScene()
        item = DiagramItem()
        item2 = DiagramItem()
        # this cause segfault
        scene.addItem(item)
        scene.addItem(item2)


if __name__ == "__main__":
    unittest.main()
