# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from math import cos, degrees, sqrt

from PySide6.QtCore import QObject, Signal, Slot, Qt
from PySide6.QtGui import QVector3D
from PySide6.QtDataVisualization import (QAbstract3DGraph, QAbstract3DSeries,
                                         QScatterDataItem, QScatterDataProxy,
                                         QScatter3DSeries, Q3DCamera,
                                         Q3DTheme)

from axesinputhandler import AxesInputHandler


NUMBER_OF_ITEMS = 10000
CURVE_DIVIDER = 7.5
LOWER_NUMBER_OF_ITEMS = 900
LOWER_CURVE_DIVIDER = 0.75


class ScatterDataModifier(QObject):

    backgroundEnabledChanged = Signal(bool)
    gridEnabledChanged = Signal(bool)
    shadowQualityChanged = Signal(int)

    def __init__(self, scatter, parent):
        super().__init__(parent)

        self._graph = scatter

        self._style = QAbstract3DSeries.MeshSphere
        self._smooth = True
        self._inputHandler = AxesInputHandler(scatter)
        self._autoAdjust = True
        self._itemCount = LOWER_NUMBER_OF_ITEMS
        self._CURVE_DIVIDER = LOWER_CURVE_DIVIDER
        self._inputHandler = AxesInputHandler(scatter)

        self._graph.activeTheme().setType(Q3DTheme.ThemeStoneMoss)
        self._graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftHigh)
        self._graph.scene().activeCamera().setCameraPreset(Q3DCamera.CameraPresetFront)
        self._graph.scene().activeCamera().setZoomLevel(80.0)

        self._proxy = QScatterDataProxy()
        self._series = QScatter3DSeries(self._proxy)
        self._series.setItemLabelFormat("@xTitle: @xLabel @yTitle: @yLabel @zTitle: @zLabel")
        self._series.setMeshSmooth(self._smooth)
        self._graph.addSeries(self._series)

        # Give ownership of the handler to the graph and make it the active
        # handler
        self._graph.setActiveInputHandler(self._inputHandler)

        # Give our axes to the input handler
        self._inputHandler.setAxes(self._graph.axisX(), self._graph.axisZ(),
                                   self._graph.axisY())

        self.addData()

    def addData(self):
        # Configure the axes according to the data
        self._graph.axisX().setTitle("X")
        self._graph.axisY().setTitle("Y")
        self._graph.axisZ().setTitle("Z")

        dataArray = []
        limit = int(sqrt(self._itemCount) / 2.0)
        for i in range(-limit, limit):
            for j in range(-limit, limit):
                x = float(i) + 0.5
                y = cos(degrees(float(i * j) / self._CURVE_DIVIDER))
                z = float(j) + 0.5
                dataArray.append(QScatterDataItem(QVector3D(x, y, z)))

        self._graph.seriesList()[0].dataProxy().resetArray(dataArray)

    @Slot(int)
    def changeStyle(self, style):
        comboBox = self.sender()
        if comboBox:
            self._style = comboBox.itemData(style)
            if self._graph.seriesList():
                self._graph.seriesList()[0].setMesh(self._style)

    @Slot(int)
    def setSmoothDots(self, smooth):
        self._smooth = smooth == Qt.Checked.value
        series = self._graph.seriesList()[0]
        series.setMeshSmooth(self._smooth)

    @Slot(int)
    def changeTheme(self, theme):
        currentTheme = self._graph.activeTheme()
        currentTheme.setType(Q3DTheme.Theme(theme))
        self.backgroundEnabledChanged.emit(currentTheme.isBackgroundEnabled())
        self.gridEnabledChanged.emit(currentTheme.isGridEnabled())

    @Slot()
    def changePresetCamera(self):
        preset = Q3DCamera.CameraPresetFrontLow.value

        camera = self._graph.scene().activeCamera()
        camera.setCameraPreset(Q3DCamera.CameraPreset(preset))

        preset += 1
        if preset > Q3DCamera.CameraPresetDirectlyBelow.value:
            preset = Q3DCamera.CameraPresetFrontLow.value

    @Slot(QAbstract3DGraph.ShadowQuality)
    def shadowQualityUpdatedByVisual(self, sq):
        self.shadowQualityChanged.emit(sq.value)

    @Slot(int)
    def changeShadowQuality(self, quality):
        sq = QAbstract3DGraph.ShadowQuality(quality)
        self._graph.setShadowQuality(sq)

    @Slot(int)
    def setBackgroundEnabled(self, enabled):
        self._graph.activeTheme().setBackgroundEnabled(enabled == Qt.Checked.value)

    @Slot(int)
    def setGridEnabled(self, enabled):
        self._graph.activeTheme().setGridEnabled(enabled == Qt.Checked.value)

    @Slot()
    def toggleItemCount(self):
        if self._itemCount == NUMBER_OF_ITEMS:
            self._itemCount = LOWER_NUMBER_OF_ITEMS
            self._CURVE_DIVIDER = LOWER_CURVE_DIVIDER
        else:
            self._itemCount = NUMBER_OF_ITEMS
            self._CURVE_DIVIDER = CURVE_DIVIDER

        self._graph.seriesList()[0].dataProxy().resetArray([])
        self.addData()

    @Slot()
    def toggleRanges(self):
        if not self._autoAdjust:
            self._graph.axisX().setAutoAdjustRange(True)
            self._graph.axisZ().setAutoAdjustRange(True)
            self._inputHandler.setDragSpeedModifier(1.5)
            self._autoAdjust = True
        else:
            self._graph.axisX().setRange(-10.0, 10.0)
            self._graph.axisZ().setRange(-10.0, 10.0)
            self._inputHandler.setDragSpeedModifier(15.0)
            self._autoAdjust = False
