# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QVector3D
from PySide6.QtDataVisualization import (QSurface3DSeries, QSurfaceDataItem)


# Value used to encode height data as RGB value on PNG file
PACKING_FACTOR = 11983.0


class TopographicSeries(QSurface3DSeries):

    def __init__(self):
        super().__init__()
        self._sampleCountX = 0.0
        self._sampleCountZ = 0.0
        self.setDrawMode(QSurface3DSeries.DrawSurface)
        self.setFlatShadingEnabled(True)
        self.setBaseColor(Qt.white)

    def sampleCountX(self):
        return self._sampleCountX

    def sampleCountZ(self):
        return self._sampleCountZ

    def setTopographyFile(self, file, width, height):
        heightMapImage = QImage(file)
        bits = heightMapImage.bits()
        imageHeight = heightMapImage.height()
        imageWidth = heightMapImage.width()
        widthBits = imageWidth * 4
        stepX = width / float(imageWidth)
        stepZ = height / float(imageHeight)

        dataArray = []
        for i in range(0, imageHeight):
            p = i * widthBits
            z = height - float(i) * stepZ
            newRow = []
            for j in range(0, imageWidth):
                aa = bits[p + 0]
                rr = bits[p + 1]
                gg = bits[p + 2]
                color = (gg << 16) + (rr << 8) + aa
                y = float(color) / PACKING_FACTOR
                item = QSurfaceDataItem(QVector3D(float(j) * stepX, y, z))
                newRow.append(item)
                p += 4
            dataArray.append(newRow)

        self.dataProxy().resetArray(dataArray)

        self._sampleCountX = float(imageWidth)
        self._sampleCountZ = float(imageHeight)
