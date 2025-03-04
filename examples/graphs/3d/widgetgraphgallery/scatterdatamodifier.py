# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import Enum
from math import sin, cos, degrees, sqrt

from PySide6.QtCore import QObject, Signal, Slot, Qt, QRandomGenerator
from PySide6.QtGui import QVector2D, QVector3D
from PySide6.QtGraphs import (QAbstract3DSeries,
                              QScatterDataItem, QScatterDataProxy,
                              QScatter3DSeries, QtGraphs3D, QGraphsTheme)


NUMBER_OF_ITEMS = 10000
CURVE_DIVIDER = 7.5
LOWER_NUMBER_OF_ITEMS = 900
LOWER_CURVE_DIVIDER = 0.75


class InputState(Enum):
    StateNormal = 0
    StateDraggingX = 1
    StateDraggingZ = 2
    StateDraggingY = 3


class ScatterDataModifier(QObject):

    backgroundVisibleChanged = Signal(bool)
    gridVisibleChanged = Signal(bool)
    shadowQualityChanged = Signal(int)

    def __init__(self, scatter, parent):
        super().__init__(parent)

        self._graph = scatter

        self._style = QAbstract3DSeries.Mesh.Sphere
        self._smooth = True
        self._autoAdjust = True
        self._itemCount = LOWER_NUMBER_OF_ITEMS
        self._CURVE_DIVIDER = LOWER_CURVE_DIVIDER

        self._graph.setShadowQuality(QtGraphs3D.ShadowQuality.SoftHigh)
        self._graph.setCameraPreset(QtGraphs3D.CameraPreset.Front)
        self._graph.setCameraZoomLevel(80.0)
        self._graph.activeTheme().setTheme(QGraphsTheme.Theme.MixSeries)
        self._graph.activeTheme().setColorScheme(QGraphsTheme.ColorScheme.Dark)

        self._proxy = QScatterDataProxy()
        self._series = QScatter3DSeries(self._proxy)
        self._series.setItemLabelFormat("@xTitle: @xLabel @yTitle: @yLabel @zTitle: @zLabel")
        self._series.setMeshSmooth(self._smooth)
        self._graph.addSeries(self._series)
        self._preset = QtGraphs3D.CameraPreset.FrontLow.value

        self._state = InputState.StateNormal
        self._dragSpeedModifier = float(15)

        self._graph.selectedElementChanged.connect(self.handleElementSelected)
        self._graph.dragged.connect(self.handleAxisDragging)
        self._graph.setDragButton(Qt.MouseButton.LeftButton)

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
        self._smooth = smooth == Qt.CheckState.Checked
        series = self._graph.seriesList()[0]
        series.setMeshSmooth(self._smooth)

    @Slot(int)
    def changeTheme(self, theme):
        currentTheme = self._graph.activeTheme()
        currentTheme.setTheme(QGraphsTheme.Theme(theme))
        self.backgroundVisibleChanged.emit(currentTheme.isPlotAreaBackgroundVisible())
        self.gridVisibleChanged.emit(currentTheme.isGridVisible())

    @Slot()
    def changePresetCamera(self):
        self._graph.setCameraPreset(QtGraphs3D.CameraPreset(self._preset))

        self._preset += 1
        if self._preset > QtGraphs3D.CameraPreset.DirectlyBelow.value:
            self._preset = QtGraphs3D.CameraPreset.FrontLow.value

    @Slot(QtGraphs3D.ShadowQuality)
    def shadowQualityUpdatedByVisual(self, sq):
        self.shadowQualityChanged.emit(sq.value)

    @Slot(QtGraphs3D.ElementType)
    def handleElementSelected(self, type):
        if type == QtGraphs3D.ElementType.AxisXLabel:
            self._state = InputState.StateDraggingX
        elif type == QtGraphs3D.ElementType.AxisYLabel:
            self._state = InputState.StateDraggingY
        elif type == QtGraphs3D.ElementType.AxisZLabel:
            self._state = InputState.StateDraggingZ
        else:
            self._state = InputState.StateNormal

    @Slot(QVector2D)
    def handleAxisDragging(self, delta):
        distance = 0.0
        # Get scene orientation from active camera
        xRotation = self._graph.cameraXRotation()
        yRotation = self._graph.cameraYRotation()

        # Calculate directional drag multipliers based on rotation
        xMulX = cos(degrees(xRotation))
        xMulY = sin(degrees(xRotation))
        zMulX = sin(degrees(xRotation))
        zMulY = cos(degrees(xRotation))

        # Get the drag amount
        move = delta.toPoint()

        # Flip the effect of y movement if we're viewing from below
        yMove = -move.y() if yRotation < 0 else move.y()

        # Adjust axes
        if self._state == InputState.StateDraggingX:
            axis = self._graph.axisX()
            distance = (move.x() * xMulX - yMove * xMulY) / self._dragSpeedModifier
            axis.setRange(axis.min() - distance, axis.max() - distance)
        elif self._state == InputState.StateDraggingZ:
            axis = self._graph.axisZ()
            distance = (move.x() * zMulX + yMove * zMulY) / self._dragSpeedModifier
            axis.setRange(axis.min() + distance, axis.max() + distance)
        elif self._state == InputState.StateDraggingY:
            axis = self._graph.axisY()
            # No need to use adjusted y move here
            distance = move.y() / self._dragSpeedModifier
            axis.setRange(axis.min() + distance, axis.max() + distance)

    @Slot(int)
    def changeShadowQuality(self, quality):
        sq = QtGraphs3D.ShadowQuality(quality)
        self._graph.setShadowQuality(sq)

    @Slot(int)
    def setBackgroundVisible(self, state):
        enabled = state == Qt.CheckState.Checked
        self._graph.activeTheme().setPlotAreaBackgroundVisible(enabled)

    @Slot(int)
    def setGridVisible(self, state):
        self._graph.activeTheme().setGridVisible(state == Qt.Checked.value)

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
            self._dragSpeedModifier = 1.5
            self._autoAdjust = True
        else:
            self._graph.axisX().setRange(-10.0, 10.0)
            self._graph.axisZ().setRange(-10.0, 10.0)
            self._dragSpeedModifier = float(15)
            self._autoAdjust = False

    def adjust_minimum_range(self, range):
        if self._itemCount == LOWER_NUMBER_OF_ITEMS:
            range *= 1.45
        else:
            range *= 4.95

        self._graph.axisX().setMin(range)
        self._graph.axisZ().setMin(range)
        self._autoAdjust = False

    def adjust_maximum_range(self, range):
        if self._itemCount == LOWER_NUMBER_OF_ITEMS:
            range *= 1.45
        else:
            range *= 4.95

        self._graph.axisX().setMax(range)
        self._graph.axisZ().setMax(range)
        self._autoAdjust = False

    def rand_vector() -> QVector3D:
        generator = QRandomGenerator.global_()
        x = float(generator.bounded(100)) / 2.0 - float(generator.bounded(100)) / 2.0
        y = float(generator.bounded(100)) / 100.0 - float(generator.bounded(100)) / 100.0
        z = float(generator.bounded(100)) / 2.0 - float(generator.bounded(100)) / 2.0
        return QVector3D(x, y, z)
