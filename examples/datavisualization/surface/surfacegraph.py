# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtDataVisualization import (Q3DTheme, QAbstract3DGraph,
                                         QHeightMapSurfaceDataProxy,
                                         QSurface3DSeries, QSurfaceDataItem,
                                         QSurfaceDataProxy, QValue3DAxis)
from PySide6.QtGui import QImage, QLinearGradient, QVector3D
from PySide6.QtWidgets import QSlider

SAMPLE_COUNT_X = 50
SAMPLE_COUNT_Z = 50
HEIGHT_MAP_GRID_STEP_X = 6
HEIGHT_MAP_GRID_STEP_Z = 6
SAMPLE_MIN = -8.0
SAMPLE_MAX = 8.0


class SurfaceGraph(QObject):
    def __init__(self, surface, parent=None):
        super().__init__(parent)

        self._graph = surface
        self._graph.setAxisX(QValue3DAxis())
        self._graph.setAxisY(QValue3DAxis())
        self._graph.setAxisZ(QValue3DAxis())

        self._sqrtSinProxy = QSurfaceDataProxy()
        self._sqrtSinSeries = QSurface3DSeries(self._sqrtSinProxy)
        self.fill_sqrt_sin_proxy()

        image_file = Path(__file__).parent / "mountain.png"
        height_map_image = QImage(image_file)
        self._heightMapProxy = QHeightMapSurfaceDataProxy(height_map_image)
        self._heightMapSeries = QSurface3DSeries(self._heightMapProxy)
        self._heightMapSeries.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        self._heightMapProxy.setValueRanges(34.0, 40.0, 18.0, 24.0)

        self._heightMapWidth = height_map_image.width()
        self._heightMapHeight = height_map_image.height()

        self._axisMinSliderX = QSlider()
        self._axisMaxSliderX = QSlider()
        self._axisMinSliderZ = QSlider()
        self._axisMaxSliderZ = QSlider()
        self._rangeMinX = 0.0
        self._rangeMinZ = 0.0
        self._stepX = 0.0
        self._stepZ = 0.0

    def fill_sqrt_sin_proxy(self):
        step_x = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_X - 1)
        step_z = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_Z - 1)

        data_array = []
        for i in range(SAMPLE_COUNT_Z):
            new_row = []
            # Keep values within range bounds, since just adding step can cause
            # minor drift due to the rounding errors.
            z = min(SAMPLE_MAX, (i * step_z + SAMPLE_MIN))
            for j in range(SAMPLE_COUNT_X):
                x = min(SAMPLE_MAX, (j * step_x + SAMPLE_MIN))
                R = math.sqrt(z * z + x * x) + 0.01
                y = (math.sin(R) / R + 0.24) * 1.61
                new_row.append(QSurfaceDataItem(QVector3D(x, y, z)))
            data_array.append(new_row)

        self._sqrtSinProxy.resetArray(data_array)

    @Slot(bool)
    def enable_sqrt_sin_model(self, enable):
        if enable:
            self._sqrtSinSeries.setDrawMode(QSurface3DSeries.DrawSurfaceAndWireframe)
            self._sqrtSinSeries.setFlatShadingEnabled(True)

            self._graph.axisX().setLabelFormat("%.2f")
            self._graph.axisZ().setLabelFormat("%.2f")
            self._graph.axisX().setRange(SAMPLE_MIN, SAMPLE_MAX)
            self._graph.axisY().setRange(0.0, 2.0)
            self._graph.axisZ().setRange(SAMPLE_MIN, SAMPLE_MAX)
            self._graph.axisX().setLabelAutoRotation(30)
            self._graph.axisY().setLabelAutoRotation(90)
            self._graph.axisZ().setLabelAutoRotation(30)

            self._graph.removeSeries(self._heightMapSeries)
            self._graph.addSeries(self._sqrtSinSeries)

            # Reset range sliders for Sqrt&Sin
            self._rangeMinX = SAMPLE_MIN
            self._rangeMinZ = SAMPLE_MIN
            self._stepX = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_X - 1)
            self._stepZ = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_Z - 1)
            self._axisMinSliderX.setMaximum(SAMPLE_COUNT_X - 2)
            self._axisMinSliderX.setValue(0)
            self._axisMaxSliderX.setMaximum(SAMPLE_COUNT_X - 1)
            self._axisMaxSliderX.setValue(SAMPLE_COUNT_X - 1)
            self._axisMinSliderZ.setMaximum(SAMPLE_COUNT_Z - 2)
            self._axisMinSliderZ.setValue(0)
            self._axisMaxSliderZ.setMaximum(SAMPLE_COUNT_Z - 1)
            self._axisMaxSliderZ.setValue(SAMPLE_COUNT_Z - 1)

    @Slot(bool)
    def enable_height_map_model(self, enable):
        if enable:
            self._heightMapSeries.setDrawMode(QSurface3DSeries.DrawSurface)
            self._heightMapSeries.setFlatShadingEnabled(False)

            self._graph.axisX().setLabelFormat("%.1f N")
            self._graph.axisZ().setLabelFormat("%.1f E")
            self._graph.axisX().setRange(34.0, 40.0)
            self._graph.axisY().setAutoAdjustRange(True)
            self._graph.axisZ().setRange(18.0, 24.0)

            self._graph.axisX().setTitle("Latitude")
            self._graph.axisY().setTitle("Height")
            self._graph.axisZ().setTitle("Longitude")

            self._graph.removeSeries(self._sqrtSinSeries)
            self._graph.addSeries(self._heightMapSeries)

            # Reset range sliders for height map
            map_grid_count_x = self._heightMapWidth / HEIGHT_MAP_GRID_STEP_X
            map_grid_count_z = self._heightMapHeight / HEIGHT_MAP_GRID_STEP_Z
            self._rangeMinX = 34.0
            self._rangeMinZ = 18.0
            self._stepX = 6.0 / float(map_grid_count_x - 1)
            self._stepZ = 6.0 / float(map_grid_count_z - 1)
            self._axisMinSliderX.setMaximum(map_grid_count_x - 2)
            self._axisMinSliderX.setValue(0)
            self._axisMaxSliderX.setMaximum(map_grid_count_x - 1)
            self._axisMaxSliderX.setValue(map_grid_count_x - 1)
            self._axisMinSliderZ.setMaximum(map_grid_count_z - 2)
            self._axisMinSliderZ.setValue(0)
            self._axisMaxSliderZ.setMaximum(map_grid_count_z - 1)
            self._axisMaxSliderZ.setValue(map_grid_count_z - 1)

    @Slot(int)
    def adjust_xmin(self, minimum):
        min_x = self._stepX * float(minimum) + self._rangeMinX

        maximum = self._axisMaxSliderX.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self._axisMaxSliderX.setValue(maximum)
        max_x = self._stepX * maximum + self._rangeMinX

        self.set_axis_xrange(min_x, max_x)

    @Slot(int)
    def adjust_xmax(self, maximum):
        max_x = self._stepX * float(maximum) + self._rangeMinX

        minimum = self._axisMinSliderX.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self._axisMinSliderX.setValue(minimum)
        min_x = self._stepX * minimum + self._rangeMinX

        self.set_axis_xrange(min_x, max_x)

    @Slot(int)
    def adjust_zmin(self, minimum):
        min_z = self._stepZ * float(minimum) + self._rangeMinZ

        maximum = self._axisMaxSliderZ.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self._axisMaxSliderZ.setValue(maximum)
        max_z = self._stepZ * maximum + self._rangeMinZ

        self.set_axis_zrange(min_z, max_z)

    @Slot(int)
    def adjust_zmax(self, maximum):
        max_x = self._stepZ * float(maximum) + self._rangeMinZ

        minimum = self._axisMinSliderZ.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self._axisMinSliderZ.setValue(minimum)
        min_x = self._stepZ * minimum + self._rangeMinZ

        self.set_axis_zrange(min_x, max_x)

    def set_axis_xrange(self, minimum, maximum):
        self._graph.axisX().setRange(minimum, maximum)

    def set_axis_zrange(self, minimum, maximum):
        self._graph.axisZ().setRange(minimum, maximum)

    @Slot(int)
    def change_theme(self, theme):
        self._graph.activeTheme().setType(Q3DTheme.Theme(theme))

    @Slot()
    def set_black_to_yellow_gradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.black)
        gr.setColorAt(0.33, Qt.blue)
        gr.setColorAt(0.67, Qt.red)
        gr.setColorAt(1.0, Qt.yellow)

        series = self._graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    @Slot()
    def set_green_to_red_gradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.darkGreen)
        gr.setColorAt(0.5, Qt.yellow)
        gr.setColorAt(0.8, Qt.red)
        gr.setColorAt(1.0, Qt.darkRed)

        series = self._graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    @Slot()
    def toggle_mode_none(self):
        self._graph.setSelectionMode(QAbstract3DGraph.SelectionNone)

    @Slot()
    def toggle_mode_item(self):
        self._graph.setSelectionMode(QAbstract3DGraph.SelectionItem)

    @Slot()
    def toggle_mode_slice_row(self):
        self._graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndRow | QAbstract3DGraph.SelectionSlice
        )

    @Slot()
    def toggle_mode_slice_column(self):
        self._graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndColumn | QAbstract3DGraph.SelectionSlice
        )

    def set_axis_min_slider_x(self, slider):
        self._axisMinSliderX = slider

    def set_axis_max_slider_x(self, slider):
        self._axisMaxSliderX = slider

    def set_axis_min_slider_z(self, slider):
        self._axisMinSliderZ = slider

    def set_axis_max_slider_z(self, slider):
        self._axisMaxSliderZ = slider
