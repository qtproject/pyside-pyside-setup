#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

import math

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtDataVisualization import (Q3DTheme, QAbstract3DGraph,
                                         QHeightMapSurfaceDataProxy,
                                         QSurface3DSeries, QSurfaceDataItem,
                                         QSurfaceDataProxy, QValue3DAxis)
from PySide6.QtGui import QImage, QLinearGradient, QVector3D
from PySide6.QtWidgets import QSlider

sampleCountX = 50
sampleCountZ = 50
heightMapGridStepX = 6
heightMapGridStepZ = 6
sampleMin = -8.0
sampleMax = 8.0


class SurfaceGraph(QObject):
    def __init__(self, surface, parent=None):
        QObject.__init__(self, parent)

        self.m_graph = surface
        self.m_graph.setAxisX(QValue3DAxis())
        self.m_graph.setAxisY(QValue3DAxis())
        self.m_graph.setAxisZ(QValue3DAxis())

        self.m_sqrtSinProxy = QSurfaceDataProxy()
        self.m_sqrtSinSeries = QSurface3DSeries(self.m_sqrtSinProxy)
        self.fillSqrtSinProxy()

        heightMapImage = QImage("mountain.png")
        self.m_heightMapProxy = QHeightMapSurfaceDataProxy(heightMapImage)
        self.m_heightMapSeries = QSurface3DSeries(self.m_heightMapProxy)
        self.m_heightMapSeries.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        self.m_heightMapProxy.setValueRanges(34.0, 40.0, 18.0, 24.0)

        self.m_heightMapWidth = heightMapImage.width()
        self.m_heightMapHeight = heightMapImage.height()

        self.m_axisMinSliderX = QSlider()
        self.m_axisMaxSliderX = QSlider()
        self.m_axisMinSliderZ = QSlider()
        self.m_axisMaxSliderZ = QSlider()
        self.m_rangeMinX = 0.0
        self.m_rangeMinZ = 0.0
        self.m_stepX = 0.0
        self.m_stepZ = 0.0

    def fillSqrtSinProxy(self):
        stepX = (sampleMax - sampleMin) / float(sampleCountX - 1)
        stepZ = (sampleMax - sampleMin) / float(sampleCountZ - 1)

        dataArray = []
        for i in range(sampleCountZ):
            newRow = []
            # Keep values within range bounds, since just adding step can cause
            # minor drift due to the rounding errors.
            z = min(sampleMax, (i * stepZ + sampleMin))
            for j in range(sampleCountX):
                x = min(sampleMax, (j * stepX + sampleMin))
                R = math.sqrt(z * z + x * x) + 0.01
                y = (math.sin(R) / R + 0.24) * 1.61
                newRow.append(QSurfaceDataItem(QVector3D(x, y, z)))
            dataArray.append(newRow)

        self.m_sqrtSinProxy.resetArray(dataArray)

    def enableSqrtSinModel(self, enable):
        if enable:
            self.m_sqrtSinSeries.setDrawMode(QSurface3DSeries.DrawSurfaceAndWireframe)
            self.m_sqrtSinSeries.setFlatShadingEnabled(True)

            self.m_graph.axisX().setLabelFormat("%.2f")
            self.m_graph.axisZ().setLabelFormat("%.2f")
            self.m_graph.axisX().setRange(sampleMin, sampleMax)
            self.m_graph.axisY().setRange(0.0, 2.0)
            self.m_graph.axisZ().setRange(sampleMin, sampleMax)
            self.m_graph.axisX().setLabelAutoRotation(30)
            self.m_graph.axisY().setLabelAutoRotation(90)
            self.m_graph.axisZ().setLabelAutoRotation(30)

            self.m_graph.removeSeries(self.m_heightMapSeries)
            self.m_graph.addSeries(self.m_sqrtSinSeries)

            # Reset range sliders for Sqrt&Sin
            self.m_rangeMinX = sampleMin
            self.m_rangeMinZ = sampleMin
            self.m_stepX = (sampleMax - sampleMin) / float(sampleCountX - 1)
            self.m_stepZ = (sampleMax - sampleMin) / float(sampleCountZ - 1)
            self.m_axisMinSliderX.setMaximum(sampleCountX - 2)
            self.m_axisMinSliderX.setValue(0)
            self.m_axisMaxSliderX.setMaximum(sampleCountX - 1)
            self.m_axisMaxSliderX.setValue(sampleCountX - 1)
            self.m_axisMinSliderZ.setMaximum(sampleCountZ - 2)
            self.m_axisMinSliderZ.setValue(0)
            self.m_axisMaxSliderZ.setMaximum(sampleCountZ - 1)
            self.m_axisMaxSliderZ.setValue(sampleCountZ - 1)

    def enableHeightMapModel(self, enable):
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
            mapGridCountX = self.m_heightMapWidth / heightMapGridStepX
            mapGridCountZ = self.m_heightMapHeight / heightMapGridStepZ
            self.m_rangeMinX = 34.0
            self.m_rangeMinZ = 18.0
            self.m_stepX = 6.0 / float(mapGridCountX - 1)
            self.m_stepZ = 6.0 / float(mapGridCountZ - 1)
            self.m_axisMinSliderX.setMaximum(mapGridCountX - 2)
            self.m_axisMinSliderX.setValue(0)
            self.m_axisMaxSliderX.setMaximum(mapGridCountX - 1)
            self.m_axisMaxSliderX.setValue(mapGridCountX - 1)
            self.m_axisMinSliderZ.setMaximum(mapGridCountZ - 2)
            self.m_axisMinSliderZ.setValue(0)
            self.m_axisMaxSliderZ.setMaximum(mapGridCountZ - 1)
            self.m_axisMaxSliderZ.setValue(mapGridCountZ - 1)

    def adjustXMin(self, minimum):
        minX = self.m_stepX * float(minimum) + self.m_rangeMinX

        maximum = self.m_axisMaxSliderX.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self.m_axisMaxSliderX.setValue(maximum)
        maxX = self.m_stepX * maximum + self.m_rangeMinX

        self.setAxisXRange(minX, maxX)

    def adjustXMax(self, maximum):
        maxX = self.m_stepX * float(maximum) + self.m_rangeMinX

        minimum = self.m_axisMinSliderX.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self.m_axisMinSliderX.setValue(minimum)
        minX = self.m_stepX * minimum + self.m_rangeMinX

        self.setAxisXRange(minX, maxX)

    def adjustZMin(self, minimum):
        minZ = self.m_stepZ * float(minimum) + self.m_rangeMinZ

        maximum = self.m_axisMaxSliderZ.value()
        if minimum >= maximum:
            maximum = minimum + 1
            self.m_axisMaxSliderZ.setValue(maximum)
        maxZ = self.m_stepZ * maximum + self.m_rangeMinZ

        self.setAxisZRange(minZ, maxZ)

    def adjustZMax(self, maximum):
        maxX = self.m_stepZ * float(maximum) + self.m_rangeMinZ

        minimum = self.m_axisMinSliderZ.value()
        if maximum <= minimum:
            minimum = maximum - 1
            self.m_axisMinSliderZ.setValue(minimum)
        minX = self.m_stepZ * minimum + self.m_rangeMinZ

        self.setAxisZRange(minX, maxX)

    def setAxisXRange(self, minimum, maximum):
        self.m_graph.axisX().setRange(minimum, maximum)

    def setAxisZRange(self, minimum, maximum):
        self.m_graph.axisZ().setRange(minimum, maximum)

    @Slot()
    def changeTheme(self, theme):
        self.m_graph.activeTheme().setType(Q3DTheme.Theme(theme))

    def setBlackToYellowGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.black)
        gr.setColorAt(0.33, Qt.blue)
        gr.setColorAt(0.67, Qt.red)
        gr.setColorAt(1.0, Qt.yellow)

        self.m_graph.seriesList()[0].setBaseGradient(gr)
        self.m_graph.seriesList()[0].setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    def setGreenToRedGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.darkGreen)
        gr.setColorAt(0.5, Qt.yellow)
        gr.setColorAt(0.8, Qt.red)
        gr.setColorAt(1.0, Qt.darkRed)

        series = self.m_graph.seriesList()[0]
        series.setBaseGradient(gr)
        series.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    def toggleModeNone(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionNone)

    def toggleModeItem(self):
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionItem)

    def toggleModeSliceRow(self):
        self.m_graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndRow | QAbstract3DGraph.SelectionSlice
        )

    def toggleModeSliceColumn(self):
        self.m_graph.setSelectionMode(
            QAbstract3DGraph.SelectionItemAndColumn | QAbstract3DGraph.SelectionSlice
        )

    def setAxisMinSliderX(self, slider):
        self.m_axisMinSliderX = slider

    def setAxisMaxSliderX(self, slider):
        self.m_axisMaxSliderX = slider

    def setAxisMinSliderZ(self, slider):
        self.m_axisMinSliderZ = slider

    def setAxisMaxSliderZ(self, slider):
        self.m_axisMaxSliderZ = slider
