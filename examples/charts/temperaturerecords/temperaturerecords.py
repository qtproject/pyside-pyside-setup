#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

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
        chart_view.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(600, 300)
    w.show()
    sys.exit(app.exec())
