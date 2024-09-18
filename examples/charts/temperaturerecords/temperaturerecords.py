# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Temperature Records example from Qt v5.x"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCharts import (QBarCategoryAxis, QBarSet, QChart, QChartView,
                              QStackedBarSeries, QValueAxis)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        low = QBarSet("Min")
        high = QBarSet("Max")
        low.append([-52, -50, -45.3, -37.0, -25.6, -8.0,
                    -6.0, -11.8, -19.7, -32.8, -43.0, -48.0])
        high.append([11.9, 12.8, 18.5, 26.5, 32.0, 34.8,
                     38.2, 34.8, 29.8, 20.4, 15.1, 11.8])

        series = QStackedBarSeries()
        series.append(low)
        series.append(high)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Temperature records in celcius")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
                      "Aug", "Sep", "Oct", "Nov", "Dec"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setTitleText("Month")
        chart.addAxis(axis_x, Qt.AlignBottom)
        axis_y = QValueAxis()
        axis_y.setRange(-52, 52)
        axis_y.setTitleText("Temperature [&deg;C]")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setCentralWidget(chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(600, 300)
    w.show()
    sys.exit(app.exec())
