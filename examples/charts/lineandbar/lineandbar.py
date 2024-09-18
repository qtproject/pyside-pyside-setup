# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the line/bar example from Qt v5.x"""

import sys
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCharts import (QBarCategoryAxis, QBarSeries, QBarSet, QChart,
                              QChartView, QLineSeries, QValueAxis)


class TestChart(QMainWindow):
    def __init__(self):
        super().__init__()

        self.set0 = QBarSet("Jane")
        self.set1 = QBarSet("John")
        self.set2 = QBarSet("Axel")
        self.set3 = QBarSet("Mary")
        self.set4 = QBarSet("Sam")

        self.set0.append([1, 2, 3, 4, 5, 6])
        self.set1.append([5, 0, 0, 4, 0, 7])
        self.set2.append([3, 5, 8, 13, 8, 5])
        self.set3.append([5, 6, 7, 3, 4, 5])
        self.set4.append([9, 7, 5, 3, 1, 2])

        self._bar_series = QBarSeries()
        self._bar_series.append(self.set0)
        self._bar_series.append(self.set1)
        self._bar_series.append(self.set2)
        self._bar_series.append(self.set3)
        self._bar_series.append(self.set4)

        self._line_series = QLineSeries()
        self._line_series.setName("trend")
        self._line_series.append(QPoint(0, 4))
        self._line_series.append(QPoint(1, 15))
        self._line_series.append(QPoint(2, 20))
        self._line_series.append(QPoint(3, 4))
        self._line_series.append(QPoint(4, 12))
        self._line_series.append(QPoint(5, 17))

        self.chart = QChart()
        self.chart.addSeries(self._bar_series)
        self.chart.addSeries(self._line_series)
        self.chart.setTitle("Line and barchart example")

        self.categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        self._axis_x = QBarCategoryAxis()
        self._axis_x.append(self.categories)
        self.chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._line_series.attachAxis(self._axis_x)
        self._bar_series.attachAxis(self._axis_x)
        self._axis_x.setRange("Jan", "Jun")

        self._axis_y = QValueAxis()
        self.chart.addAxis(self._axis_x, Qt.AlignLeft)
        self._line_series.attachAxis(self._axis_y)
        self._bar_series.attachAxis(self._axis_y)
        self._axis_y.setRange(0, 20)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setCentralWidget(self._chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TestChart()
    window.show()
    window.resize(440, 300)

    sys.exit(app.exec())
