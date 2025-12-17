# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

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
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)

        # Create QGraphView via QML
        self.series = QLineSeries()
        self.axis_x = QDateTimeAxis()
        self.axis_y = QValueAxis()
        self.quick_widget = QQuickWidget(self)
        self.quick_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self.theme = QGraphsTheme()
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
