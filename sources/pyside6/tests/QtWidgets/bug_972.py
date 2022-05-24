# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QSizeF
from PySide6.QtWidgets import QGraphicsProxyWidget, QSizePolicy, QPushButton, QGraphicsScene, QGraphicsView

from helper.timedqapplication import TimedQApplication


def createItem(minimum, preferred, maximum, name):
    w = QGraphicsProxyWidget()

    w.setWidget(QPushButton(name))
    w.setMinimumSize(minimum)
    w.setPreferredSize(preferred)
    w.setMaximumSize(maximum)
    w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    return w


class TestBug972 (TimedQApplication):

    # Test if the function QGraphicsProxyWidget.setWidget have the correct behavior
    def testIt(self):
        scene = QGraphicsScene()

        minSize = QSizeF(30, 100)
        prefSize = QSizeF(210, 100)
        maxSize = QSizeF(300, 100)

        a = createItem(minSize, prefSize, maxSize, "A")
        b = createItem(minSize, prefSize, maxSize, "B")
        c = createItem(minSize, prefSize, maxSize, "C")
        d = createItem(minSize, prefSize, maxSize, "D")

        view = QGraphicsView(scene)
        view.show()
        self.app.exec()


if __name__ == "__main__":
    unittest.main()
