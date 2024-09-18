# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import numpy as np
import math
from pathlib import Path

from PySide6.QtCore import (QAbstractTableModel, QByteArray, QModelIndex,
                            QObject, Qt, Slot)
from PySide6.QtDataVisualization import (Q3DTheme, QAbstract3DGraph,
                                         QHeightMapSurfaceDataProxy,
                                         QSurface3DSeries,
                                         QItemModelSurfaceDataProxy,
                                         QValue3DAxis)
from PySide6.QtGui import QImage, QLinearGradient
from PySide6.QtWidgets import QSlider

SAMPLE_COUNT_X = 50
SAMPLE_COUNT_Z = 50
HEIGHT_MAP_GRID_STEP_X = 6
HEIGHT_MAP_GRID_STEP_Z = 6
SAMPLE_MIN = -8.0
SAMPLE_MAX = 8.0


X_ROLE = Qt.ItemDataRole.UserRole + 1
Y_ROLE = Qt.ItemDataRole.UserRole + 2
Z_ROLE = Qt.ItemDataRole.UserRole + 3


class SqrtSinModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._x = np.zeros(SAMPLE_COUNT_X)
        self._z = np.zeros(SAMPLE_COUNT_Z)
        self._data = np.zeros((SAMPLE_COUNT_Z, SAMPLE_COUNT_X))

        step_x = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_X - 1)
        step_z = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_Z - 1)

        for i in range(SAMPLE_COUNT_Z):
            # Keep values within range bounds, since just adding step can cause
            # minor drift due to the rounding errors.
            z = min(SAMPLE_MAX, (i * step_z + SAMPLE_MIN))
            self._z[i] = z
            for j in range(SAMPLE_COUNT_X):
                x = min(SAMPLE_MAX, (j * step_x + SAMPLE_MIN))
                self._x[j] = x
                R = math.sqrt(z * z + x * x) + 0.01
                y = (math.sin(R) / R + 0.24) * 1.61
                self._data[i, j] = y

    def roleNames(self):
        result = super().roleNames()
        result[X_ROLE] = QByteArray(b"x")
        result[Y_ROLE] = QByteArray(b"y")
        result[Z_ROLE] = QByteArray(b"z")
        return result

    def rowCount(self, index=QModelIndex()):
        return self._z.size

    def columnCount(self, index=QModelIndex()):
        return self._x.size

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        row = index.row()
        col = index.column()
        if role == X_ROLE:
            return float(self._x[col])
        if role == Y_ROLE:
            return float(self._data[row][col])
        if role == Z_ROLE:
            return float(self._z[row])
        return 0.0


class SurfaceGraph(QObject):
    def __init__(self, surface, parent=None):
        super().__init__(parent)

        self.m_graph = surface
        self.m_graph.setAxisX(QValue3DAxis())
        self.m_graph.setAxisY(QValue3DAxis())
        self.m_graph.setAxisZ(QValue3DAxis())

        self.m_sqrtSinModel = SqrtSinModel(self)
        self.m_sqrtSinProxy = QItemModelSurfaceDataProxy(self.m_sqrtSinModel, self)
        self.m_sqrtSinProxy.setUseModelCategories(True)
        self.m_sqrtSinProxy.setXPosRole("x")
        self.m_sqrtSinProxy.setYPosRole("y")
        self.m_sqrtSinProxy.setZPosRole("z")

        self.m_sqrtSinSeries = QSurface3DSeries(self.m_sqrtSinProxy)

        image_file = Path(__file__).parent.parent / "surface" / "mountain.png"
        height_map_image = QImage(image_file)
        self.m_heightMapProxy = QHeightMapSurfaceDataProxy(height_map_image)
        self.m_heightMapSeries = QSurface3DSeries(self.m_heightMapProxy)
        self.m_heightMapSeries.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        self.m_heightMapProxy.setValueRanges(34.0, 40.0, 18.0, 24.0)

        self.m_heightMapWidth = height_map_image.width()
        self.m_heightMapHeight = height_map_image.height()

        self.m_axisMinSliderX = QSlider()
        self.m_axisMaxSliderX = QSlider()
        self.m_axisMinSliderZ = QSlider()
        self.m_axisMaxSliderZ = QSlider()
        self.m_rangeMinX = 0.0
        self.m_rangeMinZ = 0.0
        self.m_stepX = 0.0
        self.m_stepZ = 0.0

    @Slot(bool)
    def enable_sqrt_sin_model(self, enable):
        if enable:
            self.m_sqrtSinSeries.setDrawMode(QSurface3DSeries.DrawSurfaceAndWireframe)
            self.m_sqrtSinSeries.setFlatShadingEnabled(True)

            self.m_graph.axisX().setLabelFormat("%.2f")
            self.m_graph.axisZ().setLabelFormat("%.2f")
            self.m_graph.axisX().setRange(SAMPLE_MIN, SAMPLE_MAX)
            self.m_graph.axisY().setRange(0.0, 2.0)
            self.m_graph.axisZ().setRange(SAMPLE_MIN, SAMPLE_MAX)
            self.m_graph.axisX().setLabelAutoRotation(30)
            self.m_graph.axisY().setLabelAutoRotation(90)
            self.m_graph.axisZ().setLabelAutoRotation(30)

            self.m_graph.removeSeries(self.m_heightMapSeries)
            self.m_graph.addSeries(self.m_sqrtSinSeries)

            # Reset range sliders for Sqrt&Sin
            self.m_rangeMinX = SAMPLE_MIN
            self.m_rangeMinZ = SAMPLE_MIN
            self.m_stepX = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_X - 1)
            self.m_stepZ = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_Z - 1)
            self.m_axisMinSliderX.setMaximum(SAMPLE_COUNT_X - 2)
            self.m_axisMinSliderX.setValue(0)
            self.m_axisMaxSliderX.setMaximum(SAMPLE_COUNT_X - 1)
            self.m_axisMaxSliderX.setValue(SAMPLE_COUNT_X - 1)
            self.m_axisMinSliderZ.setMaximum(SAMPLE_COUNT_Z - 2)
            self.m_axisMinSliderZ.setValue(0)
            self.m_axisMaxSliderZ.setMaximum(SAMPLE_COUNT_Z - 1)
            self.m_axisMaxSliderZ.setValue(SAMPLE_COUNT_Z - 1)

    @Slot(bool)
    def enable_height_map_model(self, enable):
        if enable:
            self.m_heightMapSeries.setDrawMode(QSurface3DSeries.DrawSurface)
            self.m_heightMapSeries.setFlatShadingEnabled(False)

            self.m_graph.axisX().setLabelFormat("%.1f N")
            self.m_graph.axisZ().setLabelFormat("%.1f E")
            self.m_graph.axisX().setRange(34.0, 40.0)
            self.m_graph.axisY().setAutoAdjustRange(True)
            self.m_graph.axisZ().setRange(18.0, 24.0)

            self.m_graph.axisX().setTitle("Latitude")
            self.m_graph.axisY().setTitle("Height")
            self.m_graph.axisZ().setTitle("Longitude")

            self.m_graph.removeSeries(self.m_sqrtSinSeries)
            self.m_graph.addSeries(self.m_heightMapSeries)

            # Reset range sliders for height map
            map_grid_count_x = self.m_heightMapWidth / HEIGHT_MAP_GRID_STEP_X
            map_grid_count_z = self.m_heightMapHeight / HEIGHT_MAP_GRID_STEP_Z
            self.m_rangeMinX = 34.0
            self.m_rangeMinZ = 18.0
            self.m_stepX = 6.0 / float(map_grid_count_x - 1)
            self.m_stepZ = 6.0 / float(map_grid_count_z - 1)
            self.m_axisMinSliderX.setMaximum(map_grid_count_x - 2)
            self.m_axisMinSliderX.setValue(0)
            self.m_axisMaxSliderX.setMaximum(map_grid_count_x - 1)
            self.m_axisMaxSliderX.setValue(map_grid_count_x - 1)
            self.m_axisMinSliderZ.setMaximum(map_grid_count_z - 2)
            self.m_axisMinSliderZ.setValue(0)
            self.m_axisMaxSliderZ.setMaximum(map_grid_count_z - 1)
            self.m_axisMaxSliderZ.setValue(map_grid_count_z - 1)

    @Slot(int)
    def adjust_xmin(self, minimum):
        min_x = self.m_stepX * float(minimum) + self.m_rangeMinX

        maximum = self.m_axisMaxSliderX.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self.m_axisMaxSliderX.setValue(maximum)
        max_x = self.m_stepX * maximum + self.m_rangeMinX

        self.set_axis_xrange(min_x, max_x)

    @Slot(int)
    def adjust_xmax(self, maximum):
        max_x = self.m_stepX * float(maximum) + self.m_rangeMinX

        minimum = self.m_axisMinSliderX.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self.m_axisMinSliderX.setValue(minimum)
        min_x = self.m_stepX * minimum + self.m_rangeMinX

        self.set_axis_xrange(min_x, max_x)

    @Slot(int)
    def adjust_zmin(self, minimum):
        min_z = self.m_stepZ * float(minimum) + self.m_rangeMinZ

        maximum = self.m_axisMaxSliderZ.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self.m_axisMaxSliderZ.setValue(maximum)
        max_z = self.m_stepZ * maximum + self.m_rangeMinZ

        self.set_axis_zrange(min_z, max_z)

    @Slot(int)
    def adjust_zmax(self, maximum):
        max_x = self.m_stepZ * float(maximum) + self.m_rangeMinZ

        minimum = self.m_axisMinSliderZ.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self.m_axisMinSliderZ.setValue(minimum)
        min_x = self.m_stepZ * minimum + self.m_rangeMinZ

        self.set_axis_zrange(min_x, max_x)

    def set_axis_xrange(self, minimum, maximum):
        self.m_graph.axisX().setRange(minimum, maximum)

    def set_axis_zrange(self, minimum, maximum):
        self.m_graph.axisZ().setRange(minimum, maximum)

    @Slot(int)
    def change_theme(self, theme):
        self.m_graph.activeTheme().setType(Q3DTheme.Theme(theme))

    @Slot()
    def set_black_to_yellow_gradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.black)
        gr.setColorAt(0.33, Qt.blue)
        gr.setColorAt(0.67, Qt.red)
        gr.setColorAt(1.0, Qt.yellow)

        series = self.m_graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    @Slot()
    def set_green_to_red_gradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.darkGreen)
        gr.setColorAt(0.5, Qt.yellow)
        gr.setColorAt(0.8, Qt.red)
        gr.setColorAt(1.0, Qt.darkRed)

        series = self.m_graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    @Slot()
    def toggle_mode_none(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionNone)

    @Slot()
    def toggle_mode_item(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionItem)

    @Slot()
    def toggle_mode_slice_row(self):
        self.m_graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndRow | QAbstract3DGraph.SelectionSlice
        )

    @Slot()
    def toggle_mode_slice_column(self):
        self.m_graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndColumn | QAbstract3DGraph.SelectionSlice
        )

    def set_axis_min_slider_x(self, slider):
        self.m_axisMinSliderX = slider

    def set_axis_max_slider_x(self, slider):
        self.m_axisMaxSliderX = slider

    def set_axis_min_slider_z(self, slider):
        self.m_axisMinSliderZ = slider

    def set_axis_max_slider_z(self, slider):
        self.m_axisMaxSliderZ = slider
