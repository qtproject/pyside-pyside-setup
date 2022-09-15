# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import QPoint, QTimer, QTime, Qt
from PySide6.QtGui import (QColor, QGradient, QGuiApplication, QPainter,
                           QPolygon, QRasterWindow)

"""Simplified PySide6 port of the gui/analogclock example from Qt v6.x"""


class AnalogClockWindow(QRasterWindow):

    def __init__(self):
        super().__init__()
        self.setTitle("Analog Clock")
        self.resize(200, 200)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(1000)

        self._hour_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -40)])
        self._minute_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -70)])

        self._hour_color = QColor(127, 0, 127)
        self._minute_color = QColor(0, 127, 127, 191)

    def paintEvent(self, e):
        with QPainter(self) as p:
            self.render(p)

    def render(self, p):
        width = self.width()
        height = self.height()
        p.fillRect(0, 0, width, height, QGradient.NightFade)

        p.setRenderHint(QPainter.Antialiasing)
        p.translate(width / 2, height / 2)

        side = min(width, height)
        p.scale(side / 200.0, side / 200.0)
        p.setPen(Qt.NoPen)
        p.setBrush(self._hour_color)
        time = QTime.currentTime()

        p.save()
        p.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        p.drawConvexPolygon(self._hour_hand)
        p.restore()
        p.setPen(self._hour_color)

        for i in range(0, 12):
            p.drawLine(88, 0, 96, 0)
            p.rotate(30.0)

        p.setPen(Qt.NoPen)
        p.setBrush(self._minute_color)

        p.save()
        p.rotate(6.0 * (time.minute() + time.second() / 60.0))
        p.drawConvexPolygon(self._minute_hand)
        p.restore()
        p.setPen(self._minute_color)

        for j in range(0, 60):
            if (j % 5) != 0:
                p.drawLine(92, 0, 96, 0)
            p.rotate(6.0)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    clock = AnalogClockWindow()
    clock.show()
    sys.exit(app.exec())
