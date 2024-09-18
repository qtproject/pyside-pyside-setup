# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Donut Chart Breakdown example from Qt v5.x"""


import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice


class MainSlice(QPieSlice):
    def __init__(self, breakdown_series, parent=None):
        super().__init__(parent)

        self.breakdown_series = breakdown_series
        self.name = None

        self.percentageChanged.connect(self.update_label)

    def get_breakdown_series(self):
        return self.breakdown_series

    def set_name(self, name):
        self.name = name

    def name(self):
        return self.name

    @Slot()
    def update_label(self):
        p = self.percentage() * 100
        self.setLabel(f"{self.name} {p:.2f}%")


class DonutBreakdownChart(QChart):
    def __init__(self, parent=None):
        super().__init__(QChart.ChartTypeCartesian,
                         parent, Qt.WindowFlags())
        self.main_series = QPieSeries()
        self.main_series.setPieSize(0.7)
        self.addSeries(self.main_series)

    def add_breakdown_series(self, breakdown_series, color):
        font = QFont("Arial", 8)

        # add breakdown series as a slice to center pie
        main_slice = MainSlice(breakdown_series)
        main_slice.set_name(breakdown_series.name())
        main_slice.setValue(breakdown_series.sum())
        self.main_series.append(main_slice)

        # customize the slice
        main_slice.setBrush(color)
        main_slice.setLabelVisible()
        main_slice.setLabelColor(Qt.white)
        main_slice.setLabelPosition(QPieSlice.LabelInsideHorizontal)
        main_slice.setLabelFont(font)

        # position and customize the breakdown series
        breakdown_series.setPieSize(0.8)
        breakdown_series.setHoleSize(0.7)
        breakdown_series.setLabelsVisible()

        for pie_slice in breakdown_series.slices():
            color = QColor(color).lighter(115)
            pie_slice.setBrush(color)
            pie_slice.setLabelFont(font)

        # add the series to the chart
        self.addSeries(breakdown_series)

        # recalculate breakdown donut segments
        self.recalculate_angles()

        # update customize legend markers
        self.update_legend_markers()

    def recalculate_angles(self):
        angle = 0
        slices = self.main_series.slices()
        for pie_slice in slices:
            breakdown_series = pie_slice.get_breakdown_series()
            breakdown_series.setPieStartAngle(angle)
            angle += pie_slice.percentage() * 360.0  # full pie is 360.0
            breakdown_series.setPieEndAngle(angle)

    def update_legend_markers(self):
        # go through all markers
        for series in self.series():
            markers = self.legend().markers(series)
            for marker in markers:
                if series == self.main_series:
                    # hide markers from main series
                    marker.setVisible(False)
                else:
                    # modify markers from breakdown series
                    label = marker.slice().label()
                    p = marker.slice().percentage() * 100
                    marker.setLabel(f"{label} {p:.2f}%")
                    marker.setFont(QFont("Arial", 8))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Graph is based on data of:
    #    'Total consumption of energy increased by 10 per cent in 2010'
    # Statistics Finland, 13 December 2011
    # http://www.stat.fi/til/ekul/2010/ekul_2010_2011-12-13_tie_001_en.html
    series1 = QPieSeries()
    series1.setName("Fossil fuels")
    series1.append("Oil", 353295)
    series1.append("Coal", 188500)
    series1.append("Natural gas", 148680)
    series1.append("Peat", 94545)

    series2 = QPieSeries()
    series2.setName("Renewables")
    series2.append("Wood fuels", 319663)
    series2.append("Hydro power", 45875)
    series2.append("Wind power", 1060)

    series3 = QPieSeries()
    series3.setName("Others")
    series3.append("Nuclear energy", 238789)
    series3.append("Import energy", 37802)
    series3.append("Other", 32441)

    donut_breakdown = DonutBreakdownChart()
    donut_breakdown.setAnimationOptions(QChart.AllAnimations)
    donut_breakdown.setTitle("Total consumption of energy in Finland 2010")
    donut_breakdown.legend().setAlignment(Qt.AlignRight)
    donut_breakdown.add_breakdown_series(series1, Qt.red)
    donut_breakdown.add_breakdown_series(series2, Qt.darkGreen)
    donut_breakdown.add_breakdown_series(series3, Qt.darkBlue)

    window = QMainWindow()
    chart_view = QChartView(donut_breakdown)
    chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
    window.setCentralWidget(chart_view)
    available_geometry = window.screen().availableGeometry()
    size = available_geometry.height() * 0.75
    window.resize(size, size * 0.8)
    window.show()

    sys.exit(app.exec())
