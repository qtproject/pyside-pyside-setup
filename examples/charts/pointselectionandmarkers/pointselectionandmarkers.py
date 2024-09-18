# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Light Markers Points Selection example from Qt v6.2"""
import sys

from PySide6.QtCore import Slot, QPointF, Qt
from PySide6.QtCharts import QChart, QChartView, QSplineSeries
from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                               QComboBox, QCheckBox, QLabel, QHBoxLayout)

import utilities as Utilities

if __name__ == "__main__":

    a = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Light Markers and Points Selection")

    marker_size = 20.
    series = QSplineSeries()
    series.append([QPointF(0, 0),
                   QPointF(0.5, 2.27),
                   QPointF(1.5, 2.2),
                   QPointF(3.3, 1.7),
                   QPointF(4.23, 3.1),
                   QPointF(5.3, 2.3),
                   QPointF(6.47, 4.1)])
    series.setMarkerSize(marker_size)
    series.setLightMarker(Utilities.default_light_marker(marker_size))
    series.setSelectedLightMarker(Utilities.default_selected_light_marker(marker_size))

    @Slot(QPointF)
    def toggle_selection(point):
        try:
            index = series.points().index(point)
            if index != -1:
                series.toggleSelection([index])
        except ValueError:
            pass

    series.clicked.connect(toggle_selection)

    chart = QChart()
    chart.addSeries(series)
    chart.createDefaultAxes()
    chart.legend().setVisible(False)

    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

    control_widget = QWidget(window)
    control_layout = QGridLayout(control_widget)
    char_point_combobox = QComboBox()
    char_point_selected_combobox = QComboBox()
    line_color_combobox = QComboBox()
    show_unselected_points_checkbox = QCheckBox()

    @Slot(int)
    def set_light_marker(index):
        if show_unselected_points_checkbox.isChecked():
            series.setLightMarker(Utilities.get_point_representation(
                Utilities.point_type(index), marker_size))

    char_point = QLabel("Char point: ")
    char_point_combobox.addItems(["Red rectangle", "Green triangle", "Orange circle"])
    char_point_combobox.currentIndexChanged.connect(set_light_marker)

    @Slot(int)
    def set_selected_light_marker(index):
        series.setSelectedLightMarker(
            Utilities.get_selected_point_representation(
                Utilities.selected_point_type(index), marker_size))

    char_point_selected = QLabel("Char point selected: ")
    char_point_selected_combobox.addItems(["Blue triangle", "Yellow rectangle", "Lavender circle"])
    char_point_selected_combobox.currentIndexChanged.connect(set_selected_light_marker)

    @Slot(int)
    def set_line_color(index):
        series.setColor(Utilities.make_line_color(Utilities.line_color(index)))

    line_color_label = QLabel("Line color: ")
    line_color_combobox.addItems(["Blue", "Black", "Mint"])
    line_color_combobox.currentIndexChanged.connect(set_line_color)

    @Slot(int)
    def display_unselected_points(checkbox_state):
        if checkbox_state == Qt.CheckState.Checked:
            series.setLightMarker(
                Utilities.get_point_representation(
                    Utilities.point_type(char_point_combobox.currentIndex()), marker_size))
        else:
            series.setLightMarker(QImage())

    show_unselected_points_label = QLabel("Display unselected points: ")
    show_unselected_points_checkbox.setChecked(True)
    show_unselected_points_checkbox.checkStateChanged.connect(display_unselected_points)

    control_label = QLabel("Marker and Selection Controls")
    control_label.setAlignment(Qt.AlignHCenter)
    control_label_font = control_label.font()
    control_label_font.setBold(True)
    control_label.setFont(control_label_font)
    control_layout.addWidget(control_label, 0, 0, 1, 2)
    control_layout.addWidget(char_point, 1, 0)
    control_layout.addWidget(char_point_combobox, 1, 1)

    control_layout.addWidget(char_point_selected, 2, 0)
    control_layout.addWidget(char_point_selected_combobox, 2, 1)

    control_layout.addWidget(line_color_label, 3, 0)
    control_layout.addWidget(line_color_combobox, 3, 1)

    control_layout.addWidget(show_unselected_points_label, 4, 0)
    control_layout.addWidget(show_unselected_points_checkbox, 4, 1, 1, 2)
    control_layout.setRowStretch(5, 1)

    main_widget = QWidget(window)
    main_layout = QHBoxLayout(main_widget)
    main_layout.addWidget(chart_view)
    main_layout.addWidget(control_widget)

    window.setCentralWidget(main_widget)
    window.resize(1080, 720)
    window.show()
    sys.exit(a.exec())
