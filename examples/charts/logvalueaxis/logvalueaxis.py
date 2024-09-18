# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Logarithmic Axis Example from Qt v5.x"""


import sys
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCharts import (QChart, QChartView, QLineSeries, QLogValueAxis,
                              QValueAxis)


class TestChart(QMainWindow):
    def __init__(self):
        super().__init__()

        self.series = QLineSeries()
        self.series.append([
            QPointF(1.0, 1.0), QPointF(2.0, 73.0), QPointF(3.0, 268.0),
            QPointF(4.0, 17.0), QPointF(5.0, 4325.0), QPointF(6.0, 723.0)])

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().hide()
        self.chart.setTitle("Logarithmic axis example")

        self._axis_x = QValueAxis()
        self._axis_x.setTitleText("Data point")
        self._axis_x.setLabelFormat("%i")
        self._axis_x.setTickCount(self.series.count())
        self.chart.addAxis(self._axis_x, Qt.AlignBottom)
        self.series.attachAxis(self._axis_x)

        self._axis_y = QLogValueAxis()
        self._axis_y.setTitleText("Values")
        self._axis_y.setLabelFormat("%g")
        self._axis_y.setBase(8.0)
        self._axis_y.setMinorTickCount(-1)
        self.chart.addAxis(self._axis_y, Qt.AlignLeft)
        self.series.attachAxis(self._axis_y)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setCentralWidget(self._chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TestChart()
    window.show()
    window.resize(800, 600)

    sys.exit(app.exec())
