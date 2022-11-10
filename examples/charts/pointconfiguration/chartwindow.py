# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the Selected Point Configuration Example from Qt 6.5"""
from PySide6.QtCore import QObject, QPointF, Slot
from PySide6.QtGui import QColor, QIcon, QPainter
from PySide6.QtWidgets import QMainWindow, QLineEdit, QLabel, QComboBox
from PySide6.QtWidgets import QCheckBox, QWidget, QGridLayout, QHBoxLayout
from PySide6.QtCharts import QLineSeries, QXYSeries, QChart, QChartView


PointConfig = QXYSeries.PointConfiguration


class ChartWindow(QMainWindow):
    def __init__(self, parent:QObject=None ):
        super().__init__(parent)

        tr=self.tr
        self.setWindowTitle(tr("Chart"))
        self._series = QLineSeries(self)
        self._series.setName(tr("Customized series"))
        self._series.setPointsVisible(True)
        self._series.append([QPointF(0, 7), QPointF(2, 4),
            QPointF(3, 5), QPointF(7, 4), QPointF(10, 5),
            QPointF(11, 1), QPointF(13, 3), QPointF(17, 6),
            QPointF(18, 3), QPointF(20, 2)])

        selected_point_index_label = QLabel(tr("Selected Point: "))
        self._selected_point_index_lineedit = QLineEdit()
        self._selected_point_index_lineedit.setReadOnly(True)
        self._selected_point_index_lineedit.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0); border: 0px")

        color_label = QLabel(tr("Color: "))
        self._color_combobox = QComboBox()
        color_strings = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "black"]
        tr_color_strings = [tr("red"), tr("orange"), tr("yellow"), tr("green"), tr("blue"),
            tr("indigo"), tr("violet"), tr("black")]
        for i, color_str in enumerate(color_strings):
            self._color_combobox.addItem(QIcon(), tr_color_strings[i], QColor(color_str))

        size_label = QLabel(tr("Size: "))
        self._size_combobox = QComboBox()
        for size in [2, 3, 4, 6, 8, 10, 12, 15]:
            self._size_combobox.addItem(QIcon(), str(size), size)

        label_visibility_label = QLabel(tr("Label Visibility: "))
        self._label_visibility_checkbox = QCheckBox()

        custom_label_label = QLabel(tr("Custom Label: "))
        self._custom_label_lineedit = QLineEdit()

        self._series.clicked.connect(self._select_point)
        self._color_combobox.activated.connect(self._set_color)
        self._size_combobox.activated.connect(self._set_size)
        self._label_visibility_checkbox.clicked.connect(self._set_label_visibility)
        self._custom_label_lineedit.editingFinished.connect(self._set_custom_label)

        self._chart = QChart()
        self._chart.addSeries(self._series)
        self._chart.createDefaultAxes()

        chart_view = QChartView(self._chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        control_widget = QWidget(self)
        control_layout = QGridLayout(control_widget)
        control_layout.setColumnStretch(1, 1)

        control_layout.addWidget(selected_point_index_label, 0, 0)
        control_layout.addWidget(self._selected_point_index_lineedit, 0 , 1)

        control_layout.addWidget(color_label, 1, 0)
        control_layout.addWidget(self._color_combobox, 1 , 1)

        control_layout.addWidget(size_label, 2, 0)
        control_layout.addWidget(self._size_combobox, 2 , 1)

        control_layout.addWidget(label_visibility_label, 3, 0)
        control_layout.addWidget(self._label_visibility_checkbox, 3 , 1, 1, 2)

        control_layout.addWidget(custom_label_label, 4, 0)
        control_layout.addWidget(self._custom_label_lineedit, 4 , 1)

        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)
        main_layout.addWidget(chart_view)
        main_layout.setStretch(0, 1)
        main_layout.addWidget(control_widget)
        self.setCentralWidget(main_widget)

        self._series.clicked.emit(self._series.at(4))

    @Slot(QPointF)
    def _select_point(self, point: QPointF):
        try:
            index = self._series.points().index(point.toPoint())
            self._series.deselectAllPoints()
            self._series.selectPoint(index)
            self._selectedPointIndex = index
            self._selectedPointConfig = self._series.pointConfiguration(index)
            selected_point = self._series.at(index)
            self._selected_point_index_lineedit.setText("(" + str(selected_point.x()) + ", " +
                str(selected_point.y()) + ")")
            config = self._series.pointConfiguration(index)

            try:
                color = config[PointConfig.Color]
            except KeyError:
                color = self._series.color()
            if self._color_combobox.findData(color) < 0:
                self._color_combobox.addItem(color.name(), color)
            self._color_combobox.setCurrentIndex(self._color_combobox.findData(color))

            try:
                size = config[PointConfig.Size]
            except KeyError:
                size = self._series.markerSize()
            if self._size_combobox.findData(size) < 0:
                self._size_combobox.addItem(str(size), size)
            self._size_combobox.setCurrentIndex(self._size_combobox.findData(size))

            try:
                labelVisibility = config[PointConfig.LabelVisibility]
            except KeyError:
                labelVisibility = self._series.pointLabelsVisible()
            self._label_visibility_checkbox.setChecked(labelVisibility)

            try:
                customLabel = config[PointConfig.LabelFormat]
            except KeyError:
                customLabel = ""
            self._custom_label_lineedit.setText(customLabel)
        except ValueError:
            # Do nothing if the place that was clicked on wasn't a point.
            pass

    @Slot(int)
    def _set_color(self, index: int):
        self._selectedPointConfig[PointConfig.Color] = self._color_combobox.currentData()
        self._series.setPointConfiguration(self._selectedPointIndex, self._selectedPointConfig)

    @Slot(int)
    def _set_size(self, index: int):
        self._selectedPointConfig[PointConfig.Size] = self._size_combobox.currentData()
        self._series.setPointConfiguration(self._selectedPointIndex, self._selectedPointConfig)

    @Slot(bool)
    def _set_label_visibility(self, checked: bool):
        self._selectedPointConfig[PointConfig.LabelVisibility] = checked
        self._series.setPointConfiguration(self._selectedPointIndex, self._selectedPointConfig)

    @Slot()
    def _set_custom_label(self):
        self._selectedPointConfig[PointConfig.LabelFormat] = self._custom_label_lineedit.text()
        self._series.setPointConfiguration(self._selectedPointIndex, self._selectedPointConfig)
