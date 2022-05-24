#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QCharts'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QRect, QSize, QTimer
from PySide6.QtGui import QGuiApplication, QScreen
from PySide6.QtCharts import QChart, QChartView, QPieSeries


class QChartsTestCase(UsesQApplication):
    '''Tests related to QCharts'''

    def testCharts(self):
        self.series = QPieSeries()
        self.series.append("Jane", 1)
        self.series.append("Joe", 2)
        self.series.append("Andy", 3)
        self.series.append("Barbara", 4)
        self.series.append("Axel", 5)
        slice = self.series.slices()[1]
        slice.setExploded()
        slice.setLabelVisible()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        chartView = QChartView(self.chart)
        screenSize = QGuiApplication.primaryScreen().geometry().size()
        chartView.resize(screenSize / 2)
        chartView.show()
        QTimer.singleShot(500, self.app.quit)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
