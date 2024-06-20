#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QShortcut
from PySide6.QtWidgets import QApplication, QWidget


class Window(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

    def paintEvent(self, e: QPaintEvent):
        self.paint("bla")

    def paint(self, what: str, color: Qt.GlobalColor = Qt.blue):
        with QPainter(self) as p:
            p.setPen(QColor(color))
            rect = self.rect()
            w = rect.width()
            h = rect.height()
            p.drawLine(0, 0, w, h)
            p.drawLine(0, h, w, 0)
            p.drawText(rect.center(), what)

    def sum(self):
        values = [1, 2, 3]
        result = 0
        for v in values:
            result += v
        return result


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sc = QShortcut(Qt.CTRL | Qt.Key_Q, window)
    sc.activated.connect(window.close)
    window.setWindowTitle("Test")
    window.show()
    sys.exit(app.exec())
