# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import random

from PySide6.QtCharts import QChart, QSplineSeries, QValueAxis
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPen


class Chart(QChart):
    def __init__(self, parent=None):
        super().__init__(QChart.ChartTypeCartesian, parent, Qt.WindowFlags())
        self._timer = QTimer()
        self._series = QSplineSeries(self)
        self._titles = []
        self._axisX = QValueAxis()
        self._axisY = QValueAxis()
        self._step = 0
        self._x = 5
        self._y = 1

        self._timer.timeout.connect(self.handleTimeout)
        self._timer.setInterval(1000)

        green = QPen(Qt.red)
        green.setWidth(3)
        self._series.setPen(green)
        self._series.append(self._x, self._y)

        self.addSeries(self._series)
        self.addAxis(self._axisX, Qt.AlignBottom)
        self.addAxis(self._axisY, Qt.AlignLeft)

        self._series.attachAxis(self._axisX)
        self._series.attachAxis(self._axisY)
        self._axisX.setTickCount(5)
        self._axisX.setRange(0, 10)
        self._axisY.setRange(-5, 10)

        self._timer.start()

    @Slot()
    def handleTimeout(self):
        x = self.plotArea().width() / self._axisX.tickCount()
        y = (self._axisX.max() - self._axisX.min()) / self._axisX.tickCount()
        self._x += y
        self._y = random.uniform(0, 5) - 2.5
        self._series.append(self._x, self._y)
        self.scroll(x, 0)
        if self._x == 100:
            self._timer.stop()
