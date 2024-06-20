# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import Enum
from math import sin, cos, degrees

from PySide6.QtCore import Qt
from PySide6.QtDataVisualization import QAbstract3DGraph, Q3DInputHandler


class InputState(Enum):
    StateNormal = 0
    StateDraggingX = 1
    StateDraggingZ = 2
    StateDraggingY = 3


class AxesInputHandler(Q3DInputHandler):

    def __init__(self, graph, parent=None):
        super().__init__(parent)
        self._mousePressed = False
        self._state = InputState.StateNormal
        self._axisX = None
        self._axisZ = None
        self._axisY = None
        self._speedModifier = 15.0

        # Connect to the item selection signal from graph
        graph.selectedElementChanged.connect(self.handleElementSelected)

    def setAxes(self, axisX, axisZ, axisY):
        self._axisX = axisX
        self._axisZ = axisZ
        self._axisY = axisY

    def setDragSpeedModifier(self, modifier):
        self._speedModifier = modifier

    def mousePressEvent(self, event, mousePos):
        super().mousePressEvent(event, mousePos)
        if Qt.LeftButton == event.button():
            self._mousePressed = True

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
        elif type == QAbstract3DGraph.ElementAxisYLabel:
            self._state = InputState.StateDraggingY
        elif type == QAbstract3DGraph.ElementAxisZLabel:
            self._state = InputState.StateDraggingZ
        else:
            self._state = InputState.StateNormal

    def handleAxisDragging(self):
        distance = 0.0
        # Get scene orientation from active camera
        ac = self.scene().activeCamera()
        xRotation = ac.xRotation()
        yRotation = ac.yRotation()

        # Calculate directional drag multipliers based on rotation
        xMulX = cos(degrees(xRotation))
        xMulY = sin(degrees(xRotation))
        zMulX = sin(degrees(xRotation))
        zMulY = cos(degrees(xRotation))

        # Get the drag amount
        move = self.inputPosition() - self.previousInputPos()

        # Flip the effect of y movement if we're viewing from below
        yMove = -move.y() if yRotation < 0 else move.y()

        # Adjust axes
        if self._state == InputState.StateDraggingX:
            distance = (move.x() * xMulX - yMove * xMulY) / self._speedModifier
            self._axisX.setRange(self._axisX.min() - distance,
                                 self._axisX.max() - distance)
        elif self._state == InputState.StateDraggingZ:
            distance = (move.x() * zMulX + yMove * zMulY) / self._speedModifier
            self._axisZ.setRange(self._axisZ.min() + distance,
                                 self._axisZ.max() + distance)
        elif self._state == InputState.StateDraggingY:
            # No need to use adjusted y move here
            distance = move.y() / self._speedModifier
            self._axisY.setRange(self._axisY.min() + distance,
                                 self._axisY.max() + distance)
