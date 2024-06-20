# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Slot
from PySide6.QtGui import QLinearGradient, QVector3D
from PySide6.QtDataVisualization import (QSurface3DSeries, QSurfaceDataItem, Q3DTheme)


DARK_RED_POS = 1.0
RED_POS = 0.8
YELLOW_POS = 0.6
GREEN_POS = 0.4
DARK_GREEN_POS = 0.2


class HighlightSeries(QSurface3DSeries):

    def __init__(self):
        super().__init__()
        self._width = 100
        self._height = 100
        self._srcWidth = 0
        self._srcHeight = 0
        self._position = {}
        self._topographicSeries = None
        self._minHeight = 0.0
        self.setDrawMode(QSurface3DSeries.DrawSurface)
        self.setFlatShadingEnabled(True)
        self.setVisible(False)

    def setTopographicSeries(self, series):
        self._topographicSeries = series
        array = self._topographicSeries.dataProxy().array()
        self._srcWidth = len(array[0])
        self._srcHeight = len(array)
        self._topographicSeries.selectedPointChanged.connect(self.handlePositionChange)

    def setMinHeight(self, height):
        self. m_minHeight = height

    @Slot(QPoint)
    def handlePositionChange(self, position):
        self._position = position

        if position == self.invalidSelectionPosition():
            self.setVisible(False)
            return

        halfWidth = self._width / 2
        halfHeight = self._height / 2

        startX = position.y() - halfWidth
        if startX < 0:
            startX = 0
        endX = position.y() + halfWidth
        if endX > (self._srcWidth - 1):
            endX = self._srcWidth - 1
        startZ = position.x() - halfHeight
        if startZ < 0:
            startZ = 0
        endZ = position.x() + halfHeight
        if endZ > (self._srcHeight - 1):
            endZ = self._srcHeight - 1

        srcProxy = self._topographicSeries.dataProxy()
        srcArray = srcProxy.array()

        dataArray = []
        for i in range(int(startZ), int(endZ)):
            newRow = []
            srcRow = srcArray[i]
            for j in range(startX, endX):
                pos = srcRow.at(j).position()
                pos.setY(pos.y() + 0.1)
                item = QSurfaceDataItem(QVector3D(pos))
                newRow.append(item)
            dataArray.append(newRow)
        self.dataProxy().resetArray(dataArray)
        self.setVisible(True)

    @Slot(float)
    def handleGradientChange(self, value):
        ratio = self._minHeight / value

        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.black)
        gr.setColorAt(DARK_GREEN_POS * ratio, Qt.darkGreen)
        gr.setColorAt(GREEN_POS * ratio, Qt.green)
        gr.setColorAt(YELLOW_POS * ratio, Qt.yellow)
        gr.setColorAt(RED_POS * ratio, Qt.red)
        gr.setColorAt(DARK_RED_POS * ratio, Qt.darkRed)

        self.setBaseGradient(gr)
        self.setColorStyle(Q3DTheme.ColorStyleRangeGradient)
