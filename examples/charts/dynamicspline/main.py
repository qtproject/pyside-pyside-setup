# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Dynamic Spline example from Qt v5.x"""
import sys

from PySide6.QtCharts import QChart, QChartView
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QMainWindow

from chart import Chart

if __name__ == "__main__":

    a = QApplication(sys.argv)
    window = QMainWindow()
    chart = Chart()
    chart.setTitle("Dynamic spline chart")
    chart.legend().hide()
    chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
    window.setCentralWidget(chart_view)
    window.resize(400, 300)
    window.show()

    sys.exit(a.exec())
