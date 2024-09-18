# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the areachart example from Qt v6.x"""

import sys
from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QAreaSeries
from PySide6.QtGui import QGradient, QPen, QLinearGradient, QPainter


class TestChart(QMainWindow):
    def __init__(self):
        super().__init__()

        self.series_0 = QLineSeries()
        self.series_1 = QLineSeries()

        self.series_0.append(QPointF(1, 5))
        self.series_0.append(QPointF(3, 7))
        self.series_0.append(QPointF(7, 6))
        self.series_0.append(QPointF(9, 7))
        self.series_0.append(QPointF(12, 6))
        self.series_0.append(QPointF(16, 7))
        self.series_0.append(QPointF(18, 5))

        self.series_1.append(QPointF(1, 3))
        self.series_1.append(QPointF(3, 4))
        self.series_1.append(QPointF(7, 3))
        self.series_1.append(QPointF(8, 2))
        self.series_1.append(QPointF(12, 3))
        self.series_1.append(QPointF(16, 4))
        self.series_1.append(QPointF(18, 3))

        self.series = QAreaSeries(self.series_0, self.series_1)
        self.series.setName("Batman")
        self.pen = QPen(0x059605)
        self.pen.setWidth(3)
        self.series.setPen(self.pen)

        self.gradient = QLinearGradient(QPointF(0, 0), QPointF(0, 1))
        self.gradient.setColorAt(0.0, 0x3cc63c)
        self.gradient.setColorAt(1.0, 0x26f626)
        self.gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        self.series.setBrush(self.gradient)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Simple areachart example")
        self.chart.createDefaultAxes()
        self.chart.axes(Qt.Orientation.Horizontal)[0].setRange(0, 20)
        self.chart.axes(Qt.Vertical)[0].setRange(0, 10)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setCentralWidget(self._chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TestChart()
    window.show()
    window.resize(400, 300)
    sys.exit(app.exec())
