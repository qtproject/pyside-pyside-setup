# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from math import sin, pi

from PySide6.QtCore import QObject, QRandomGenerator, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QVector3D
from PySide6.QtDataVisualization import QSurfaceDataItem, QSurface3DSeries


QML_IMPORT_NAME = "SurfaceGallery"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class DataSource(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_index = -1
        self.m_resetArray = None
        self.m_data = []

    @Slot(int, int, int, float, float, float, float, float, float)
    def generateData(self, cacheCount, rowCount, columnCount,
                     xMin, xMax, yMin, yMax, zMin, zMax):
        if not cacheCount or not rowCount or not columnCount:
            return

        self.clearData()

        xRange = xMax - xMin
        yRange = yMax - yMin
        zRange = zMax - zMin
        cacheIndexStep = columnCount / cacheCount
        cacheStep = float(cacheIndexStep) * xRange / float(columnCount)

        # Populate caches
        self.m_data = []
        rand_gen = QRandomGenerator.global_()
        for i in range(0, cacheCount):
            cache = []
            cacheXAdjustment = cacheStep * i
            cacheIndexAdjustment = cacheIndexStep * i
            for j in range(0, rowCount):
                row = []
                rowMod = (float(j)) / float(rowCount)
                yRangeMod = yRange * rowMod
                zRangeMod = zRange * rowMod
                z = zRangeMod + zMin
                rowColWaveAngleMul = pi * pi * rowMod
                rowColWaveMul = yRangeMod * 0.2
                for k in range(0, columnCount):
                    colMod = (float(k)) / float(columnCount)
                    xRangeMod = xRange * colMod
                    x = xRangeMod + xMin + cacheXAdjustment
                    colWave = sin((2.0 * pi * colMod) - (1.0 / 2.0 * pi)) + 1.0
                    rand_nr = rand_gen.generateDouble() * 0.15
                    y = ((colWave * ((sin(rowColWaveAngleMul * colMod) + 1.0)))
                         * rowColWaveMul + rand_nr * yRangeMod)

                    index = k + cacheIndexAdjustment
                    if index >= columnCount:
                        # Wrap over
                        index -= columnCount
                        x -= xRange

                    row.append(QSurfaceDataItem(QVector3D(x, y, z)))
                cache.append(row)
            self.m_data.append(cache)

    @Slot(QSurface3DSeries)
    def update(self, series):
        if series and self.m_data:
            # Each iteration uses data from a different cached array
            self.m_index += 1
            if self.m_index > len(self.m_data) - 1:
                self.m_index = 0

            array = self.m_data[self.m_index]
            newRowCount = len(array)
            newColumnCount = len(array[0])

            # Copy items from our cache to the reset array
            self.m_resetArray = []
            for i in range(0, newRowCount):
                sourceRow = array[i]
                row = []
                for j in range(0, newColumnCount):
                    row.append(QSurfaceDataItem(sourceRow[j].position()))
                self.m_resetArray.append(row)

            # Notify the proxy that data has changed
            series.dataProxy().resetArray(self.m_resetArray)

    @Slot()
    def clearData(self):
        self.m_data = []
