# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Nested Donuts example from Qt v5.x"""

import sys

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QGridLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice


from random import randrange
from functools import partial


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.donuts = []
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart = self.chart_view.chart()
        self.chart.legend().setVisible(False)
        self.chart.setTitle("Nested donuts demo")
        self.chart.setAnimationOptions(QChart.AllAnimations)

        self.min_size = 0.1
        self.max_size = 0.9
        self.donut_count = 5

        self.setup_donuts()

        # create main layout
        self.main_layout = QGridLayout(self)
        self.main_layout.addWidget(self.chart_view, 1, 1)
        self.setLayout(self.main_layout)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_rotation)
        self.update_timer.start(1250)

    def setup_donuts(self):
        for i in range(self.donut_count):
            donut = QPieSeries()
            slccount = randrange(3, 6)
            for j in range(slccount):
                value = randrange(100, 200)

                slc = QPieSlice(str(value), value)
                slc.setLabelVisible(True)
                slc.setLabelColor(Qt.white)
                slc.setLabelPosition(QPieSlice.LabelInsideTangential)

                # Connection using an extra parameter for the slot
                slc.hovered[bool].connect(partial(self.explode_slice, slc=slc))

                donut.append(slc)
                size = (self.max_size - self.min_size) / self.donut_count
                donut.setHoleSize(self.min_size + i * size)
                donut.setPieSize(self.min_size + (i + 1) * size)

            self.donuts.append(donut)
            self.chart_view.chart().addSeries(donut)

    @Slot()
    def update_rotation(self):
        for donut in self.donuts:
            phase_shift = randrange(-50, 100)
            donut.setPieStartAngle(donut.pieStartAngle() + phase_shift)
            donut.setPieEndAngle(donut.pieEndAngle() + phase_shift)

    def explode_slice(self, exploded, slc):
        if exploded:
            self.update_timer.stop()
            slice_startangle = slc.startAngle()
            slice_endangle = slc.startAngle() + slc.angleSpan()

            donut = slc.series()
            idx = self.donuts.index(donut)
            for i in range(idx + 1, len(self.donuts)):
                self.donuts[i].setPieStartAngle(slice_endangle)
                self.donuts[i].setPieEndAngle(360 + slice_startangle)
        else:
            for donut in self.donuts:
                donut.setPieStartAngle(0)
                donut.setPieEndAngle(360)

            self.update_timer.start()

        slc.setExploded(exploded)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec())
