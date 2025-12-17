# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from math import floor, ceil

from PySide6.QtCore import QDateTime, QTime, QTimeZone
from PySide6.QtWidgets import (QWidget, QHeaderView, QHBoxLayout, QTableView,
                               QSizePolicy)
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtGraphs import QLineSeries, QDateTimeAxis, QValueAxis, QGraphsTheme

from table_model import CustomTableModel


class Widget(QWidget):
    def __init__(self, data):
        super().__init__()

        # Getting the Model
        self.model = CustomTableModel(data)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # QTableView Headers
        resize = QHeaderView.ResizeMode.ResizeToContents
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(resize)
        self.vertical_header.setSectionResizeMode(resize)
        self.horizontal_header.setStretchLastSection(True)

        # Create QGraphView via QML
        self.populate_series()
        self.quick_widget = QQuickWidget(self)
        self.quick_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self.theme = QGraphsTheme()
        self.theme.setTheme(QGraphsTheme.Theme.BlueSeries)
        initial_properties = {"theme": self.theme,
                              "axisX": self.axis_x,
                              "axisY": self.axis_y,
                              "seriesList": self.series}
        self.quick_widget.setInitialProperties(initial_properties)
        self.quick_widget.loadFromModule("QtGraphs", "GraphsView")

        # QWidget Layout
        self.main_layout = QHBoxLayout(self)
        size = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Right Layout
        size.setHorizontalStretch(4)
        self.quick_widget.setSizePolicy(size)
        self.main_layout.addWidget(self.quick_widget)

    def populate_series(self):
        def seconds(qtime: QTime):
            return qtime.minute() * 60 + qtime.second()

        self.series = QLineSeries()
        self.series.setName("Magnitude (Column 1)")

        # Filling QLineSeries
        time_min = QDateTime(2100, 1, 1, 0, 0, 0)
        time_max = QDateTime(1970, 1, 1, 0, 0, 0)
        time_zone = QTimeZone(QTimeZone.Initialization.UTC)
        y_min = 1e37
        y_max = -1e37
        date_fmt = "yyyy-MM-dd HH:mm:ss.zzz"
        for i in range(self.model.rowCount()):
            t = self.model.index(i, 0).data()
            time = QDateTime.fromString(t, date_fmt)
            time.setTimeZone(time_zone)
            y = float(self.model.index(i, 1).data())
            if time.isValid() and y > 0:
                if time > time_max:
                    time_max = time
                if time < time_min:
                    time_min = time
                if y > y_max:
                    y_max = y
                if y < y_min:
                    y_min = y
                self.series.append(time.toMSecsSinceEpoch(), y)

        # Setting X-axis
        self.axis_x = QDateTimeAxis()
        self.axis_x.setLabelFormat("dd.MM (h:mm)")
        self.axis_x.setTitleText("Date")
        self.axis_x.setMin(time_min.addSecs(-seconds(time_min.time())))
        self.axis_x.setMax(time_max.addSecs(3600 - seconds(time_max.time())))
        self.series.setAxisX(self.axis_x)

        # Setting Y-axis
        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Magnitude")
        self.axis_y.setMin(floor(y_min))
        self.axis_y.setMax(ceil(y_max))
        self.series.setAxisY(self.axis_y)
