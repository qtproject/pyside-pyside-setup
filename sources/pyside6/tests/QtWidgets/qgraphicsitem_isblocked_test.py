#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QColor
from helper.usesqapplication import UsesQApplication


class Item(QGraphicsItem):

    def __init__(self):
        super().__init__()

    def boundingRect(self):
        return QRectF(0, 0, 100, 100)

    def paint(self, painter, option, widget):
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(0, 0, 100, 100)


class QGraphicsViewIsBlockedTest(UsesQApplication):

    def testIsBlockedByModalPanel(self):
        (first, second) = Item().isBlockedByModalPanel()
        self.assertFalse(first)


if __name__ == "__main__":
    unittest.main()
