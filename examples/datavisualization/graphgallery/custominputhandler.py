# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import Enum
from math import sin, cos, degrees

from PySide6.QtCore import Qt
from PySide6.QtDataVisualization import (QAbstract3DGraph, Q3DInputHandler)


class InputState(Enum):
    StateNormal = 0
    StateDraggingX = 1
    StateDraggingZ = 2
    StateDraggingY = 3


class CustomInputHandler(Q3DInputHandler):

    def __init__(self, graph, parent=None):
        super().__init__(parent)
        self._highlight = None
        self._mousePressed = False
        self._state = InputState.StateNormal
        self._axisX = None
        self._axisY = None
        self._axisZ = None
        self._speedModifier = 20.0
        self._aspectRatio = 0.0
        self._axisXMinValue = 0.0
        self._axisXMaxValue = 0.0
        self._axisXMinRange = 0.0
        self._axisZMinValue = 0.0
        self._axisZMaxValue = 0.0
        self._axisZMinRange = 0.0
        self._areaMinValue = 0.0
        self._areaMaxValue = 0.0

        # Connect to the item selection signal from graph
        graph.selectedElementChanged.connect(self.handleElementSelected)

    def setAspectRatio(self, ratio):
        self._aspectRatio = ratio

    def setHighlightSeries(self, series):
        self._highlight = series

    def setDragSpeedModifier(self, modifier):
        self._speedModifier = modifier

    def setLimits(self, min, max, minRange):
        self._areaMinValue = min
        self._areaMaxValue = max
        self._axisXMinValue = self._areaMinValue
        self._axisXMaxValue = self._areaMaxValue
        self._axisZMinValue = self._areaMinValue
        self._axisZMaxValue = self._areaMaxValue
        self._axisXMinRange = minRange
        self._axisZMinRange = minRange

    def setAxes(self, axisX, axisY, axisZ):
        self._axisX = axisX
        self._axisY = axisY
        self._axisZ = axisZ

    def mousePressEvent(self, event, mousePos):
        if Qt.LeftButton == event.button():
            self._highlight.setVisible(False)
            self._mousePressed = True
        super().mousePressEvent(event, mousePos)

    def wheelEvent(self, event):
        delta = float(event.angleDelta().y())

        self._axisXMinValue += delta
        self._axisXMaxValue -= delta
        self._axisZMinValue += delta
        self._axisZMaxValue -= delta
        self.checkConstraints()

        y = (self._axisXMaxValue - self._axisXMinValue) * self._aspectRatio

        self._axisX.setRange(self._axisXMinValue, self._axisXMaxValue)
        self._axisY.setRange(100.0, y)
        self._axisZ.setRange(self._axisZMinValue, self._axisZMaxValue)

    def mouseMoveEvent(self, event, mousePos):
        # Check if we're trying to drag axis label
        if self._mousePressed and self._state != InputState.StateNormal:
            self.setPreviousInputPos(self.inputPosition())
            self.setInputPosition(mousePos)
            self.handleAxisDragging()
        else:
            super().mouseMoveEvent(event, mousePos)

    def mouseReleaseEvent(self, event, mousePos):
        super().mouseReleaseEvent(event, mousePos)
        self._mousePressed = False
        self._state = InputState.StateNormal

    def handleElementSelected(self, type):
        if type == QAbstract3DGraph.ElementAxisXLabel:
            self._state = InputState.StateDraggingX
        elif type == QAbstract3DGraph.ElementAxisZLabel:
            self._state = InputState.StateDraggingZ
        else:
            self._state = InputState.StateNormal

    def handleAxisDragging(self):
        distance = 0.0

        # Get scene orientation from active camera
        xRotation = self.scene().activeCamera().xRotation()

        # Calculate directional drag multipliers based on rotation
        xMulX = cos(degrees(xRotation))
        xMulY = sin(degrees(xRotation))
        zMulX = xMulY
        zMulY = xMulX

        # Get the drag amount
        move = self.inputPosition() - self.previousInputPos()

        # Adjust axes
        if self._state == InputState.StateDraggingX:
            distance = (move.x() * xMulX - move.y() * xMulY) * self._speedModifier
            self._axisXMinValue -= distance
            self._axisXMaxValue -= distance
            if self._axisXMinValue < self._areaMinValue:
                dist = self._axisXMaxValue - self._axisXMinValue
                self._axisXMinValue = self._areaMinValue
                self._axisXMaxValue = self._axisXMinValue + dist

            if self._axisXMaxValue > self._areaMaxValue:
                dist = self._axisXMaxValue - self._axisXMinValue
                self._axisXMaxValue = self._areaMaxValue
                self._axisXMinValue = self._axisXMaxValue - dist

            self._axisX.setRange(self._axisXMinValue, self._axisXMaxValue)
        elif self._state == InputState.StateDraggingZ:
            distance = (move.x() * zMulX + move.y() * zMulY) * self._speedModifier
            self._axisZMinValue += distance
            self._axisZMaxValue += distance
            if self._axisZMinValue < self._areaMinValue:
                dist = self._axisZMaxValue - self._axisZMinValue
                self._axisZMinValue = self._areaMinValue
                self._axisZMaxValue = self._axisZMinValue + dist

            if self._axisZMaxValue > self._areaMaxValue:
                dist = self._axisZMaxValue - self._axisZMinValue
                self._axisZMaxValue = self._areaMaxValue
                self._axisZMinValue = self._axisZMaxValue - dist

            self._axisZ.setRange(self._axisZMinValue, self._axisZMaxValue)

    def checkConstraints(self):
        if self._axisXMinValue < self._areaMinValue:
            self._axisXMinValue = self._areaMinValue
        if self._axisXMaxValue > self._areaMaxValue:
            self._axisXMaxValue = self._areaMaxValue
        # Don't allow too much zoom in
        range = self._axisXMaxValue - self._axisXMinValue
        if range < self._axisXMinRange:
            adjust = (self._axisXMinRange - range) / 2.0
            self._axisXMinValue -= adjust
            self._axisXMaxValue += adjust

        if self._axisZMinValue < self._areaMinValue:
            self._axisZMinValue = self._areaMinValue
        if self._axisZMaxValue > self._areaMaxValue:
            self._axisZMaxValue = self._areaMaxValue
        # Don't allow too much zoom in
        range = self._axisZMaxValue - self._axisZMinValue
        if range < self._axisZMinRange:
            adjust = (self._axisZMinRange - range) / 2.0
            self._axisZMinValue -= adjust
            self._axisZMaxValue += adjust
