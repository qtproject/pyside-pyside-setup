# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit test for QBackingStore, QRasterWindow and QStaticText'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QEvent, QPoint, QRect, QSize, QTimer, Qt
from PySide6.QtGui import QColor, QBackingStore, QPaintDevice, QPainter, QWindow, QPaintDeviceWindow, QRasterWindow, QRegion, QStaticText


# Window using convenience class QRasterWindow
class TestRasterWindow(QRasterWindow):
    def __init__(self):
        super().__init__()
        self.text = QStaticText("QRasterWindow")

    def paintEvent(self, event):
        clientRect = QRect(QPoint(0, 0), self.size())
        with QPainter(self) as painter:
            painter.fillRect(clientRect, QColor(Qt.red))
            painter.drawStaticText(QPoint(10, 10), self.text)


class QRasterWindowTest(UsesQApplication):
    def test(self):
        rasterWindow = TestRasterWindow()
        rasterWindow.setFramePosition(QPoint(100, 100))
        rasterWindow.resize(QSize(400, 400))
        rasterWindow.show()
        QTimer.singleShot(100, self.app.quit)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
