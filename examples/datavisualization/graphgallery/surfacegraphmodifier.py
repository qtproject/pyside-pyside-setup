# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
from math import sqrt, sin
from pathlib import Path

from PySide6.QtCore import QObject, QPropertyAnimation, Qt, Slot
from PySide6.QtGui import (QColor, QFont, QImage, QLinearGradient,
                           QQuaternion, QVector3D)
from PySide6.QtDataVisualization import (QAbstract3DGraph, QCustom3DItem,
                                         QCustom3DLabel,
                                         QHeightMapSurfaceDataProxy,
                                         QValue3DAxis, QSurfaceDataItem,
                                         QSurfaceDataProxy, QSurface3DSeries,
                                         Q3DInputHandler, Q3DCamera, Q3DTheme)


from highlightseries import HighlightSeries
from topographicseries import TopographicSeries
from custominputhandler import CustomInputHandler


SAMPLE_COUNT_X = 150
SAMPLE_COUNT_Z = 150
HEIGHTMAP_GRID_STEP_X = 6
HEIGHTMAP_GRID_STEP_Z = 6
SAMPLE_MIN = -8.0
SAMPLE_MAX = 8.0

AREA_WIDTH = 8000.0
AREA_HEIGHT = 8000.0
ASPECT_RATIO = 0.1389
MIN_RANGE = AREA_WIDTH * 0.49


class SurfaceGraphModifier(QObject):

    def __init__(self, surface, label, parent):
        super().__init__(parent)
        self._data_path = Path(__file__).resolve().parent / "data"
        self._graph = surface
        self._textField = label
        self._sqrtSinProxy = None
        self._sqrtSinSeries = None
        self._heightMapProxyOne = None
        self._heightMapProxyTwo = None
        self._heightMapProxyThree = None
        self._heightMapSeriesOne = None
        self._heightMapSeriesTwo = None
        self._heightMapSeriesThree = None

        self._axisMinSliderX = None
        self._axisMaxSliderX = None
        self._axisMinSliderZ = None
        self._axisMaxSliderZ = None
        self._rangeMinX = 0.0
        self._rangeMinZ = 0.0
        self._stepX = 0.0
        self._stepZ = 0.0
        self._heightMapWidth = 0
        self._heightMapHeight = 0

        self._selectionAnimation = None
        self._titleLabel = None
        self._previouslyAnimatedItem = None
        self._previousScaling = {}

        self._topography = None
        self._highlight = None
        self._highlightWidth = 0
        self._highlightHeight = 0

        self._customInputHandler = None
        self._defaultInputHandler = Q3DInputHandler()

        ac = self._graph.scene().activeCamera()
        ac.setZoomLevel(85.0)
        ac.setCameraPreset(Q3DCamera.CameraPresetIsometricRight)
        self._graph.activeTheme().setType(Q3DTheme.ThemeRetro)

        self._x_axis = QValue3DAxis()
        self._y_axis = QValue3DAxis()
        self._z_axis = QValue3DAxis()
        self._graph.setAxisX(self._x_axis)
        self._graph.setAxisY(self._y_axis)
        self._graph.setAxisZ(self._z_axis)

        #
        # Sqrt Sin
        #
        self._sqrtSinProxy = QSurfaceDataProxy()
        self._sqrtSinSeries = QSurface3DSeries(self._sqrtSinProxy)
        self.fillSqrtSinProxy()

        #
        # Multisurface heightmap
        #
        # Create the first surface layer
        heightMapImageOne = QImage(self._data_path / "layer_1.png")
        self._heightMapProxyOne = QHeightMapSurfaceDataProxy(heightMapImageOne)
        self._heightMapSeriesOne = QSurface3DSeries(self._heightMapProxyOne)
        self._heightMapSeriesOne.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        self._heightMapProxyOne.setValueRanges(34.0, 40.0, 18.0, 24.0)

        # Create the other 2 surface layers
        heightMapImageTwo = QImage(self._data_path / "layer_2.png")
        self._heightMapProxyTwo = QHeightMapSurfaceDataProxy(heightMapImageTwo)
        self._heightMapSeriesTwo = QSurface3DSeries(self._heightMapProxyTwo)
        self._heightMapSeriesTwo.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        self._heightMapProxyTwo.setValueRanges(34.0, 40.0, 18.0, 24.0)

        heightMapImageThree = QImage(self._data_path / "layer_3.png")
        self._heightMapProxyThree = QHeightMapSurfaceDataProxy(heightMapImageThree)
        self._heightMapSeriesThree = QSurface3DSeries(self._heightMapProxyThree)
        self._heightMapSeriesThree.setItemLabelFormat("(@xLabel, @zLabel): @yLabel")
        self._heightMapProxyThree.setValueRanges(34.0, 40.0, 18.0, 24.0)

        # The images are the same size, so it's enough to get the dimensions
        # from one
        self._heightMapWidth = heightMapImageOne.width()
        self._heightMapHeight = heightMapImageOne.height()

        # Set the gradients for multi-surface layers
        grOne = QLinearGradient()
        grOne.setColorAt(0.0, Qt.black)
        grOne.setColorAt(0.38, Qt.darkYellow)
        grOne.setColorAt(0.39, Qt.darkGreen)
        grOne.setColorAt(0.5, Qt.darkGray)
        grOne.setColorAt(1.0, Qt.gray)
        self._heightMapSeriesOne.setBaseGradient(grOne)
        self._heightMapSeriesOne.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

        grTwo = QLinearGradient()
        grTwo.setColorAt(0.39, Qt.blue)
        grTwo.setColorAt(0.4, Qt.white)
        self._heightMapSeriesTwo.setBaseGradient(grTwo)
        self._heightMapSeriesTwo.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

        grThree = QLinearGradient()
        grThree.setColorAt(0.0, Qt.white)
        grThree.setColorAt(0.05, Qt.black)
        self._heightMapSeriesThree.setBaseGradient(grThree)
        self._heightMapSeriesThree.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

        # Custom items and label
        self._graph.selectedElementChanged.connect(self.handleElementSelected)

        self._selectionAnimation = QPropertyAnimation(self)
        self._selectionAnimation.setPropertyName(b"scaling")
        self._selectionAnimation.setDuration(500)
        self._selectionAnimation.setLoopCount(-1)

        titleFont = QFont("Century Gothic", 30)
        titleFont.setBold(True)
        self._titleLabel = QCustom3DLabel("Oil Rigs on Imaginary Sea", titleFont,
                                          QVector3D(0.0, 1.2, 0.0),
                                          QVector3D(1.0, 1.0, 0.0),
                                          QQuaternion())
        self._titleLabel.setPositionAbsolute(True)
        self._titleLabel.setFacingCamera(True)
        self._titleLabel.setBackgroundColor(QColor(0x66cdaa))
        self._graph.addCustomItem(self._titleLabel)
        self._titleLabel.setVisible(False)

        # Make two of the custom object visible
        self.toggleItemOne(True)
        self.toggleItemTwo(True)

        #
        # Topographic map
        #
        self._topography = TopographicSeries()
        file_name = os.fspath(self._data_path / "topography.png")
        self._topography.setTopographyFile(file_name, AREA_WIDTH, AREA_HEIGHT)
        self._topography.setItemLabelFormat("@yLabel m")

        self._highlight = HighlightSeries()
        self._highlight.setTopographicSeries(self._topography)
        self._highlight.setMinHeight(MIN_RANGE * ASPECT_RATIO)
        self._highlight.handleGradientChange(AREA_WIDTH * ASPECT_RATIO)
        self._graph.axisY().maxChanged.connect(self._highlight.handleGradientChange)

        self._customInputHandler = CustomInputHandler(self._graph)
        self._customInputHandler.setHighlightSeries(self._highlight)
        self._customInputHandler.setAxes(self._x_axis, self._y_axis, self._z_axis)
        self._customInputHandler.setLimits(0.0, AREA_WIDTH, MIN_RANGE)
        self._customInputHandler.setAspectRatio(ASPECT_RATIO)

    def fillSqrtSinProxy(self):
        stepX = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_X - 1)
        stepZ = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_Z - 1)

        dataArray = []
        for i in range(0, SAMPLE_COUNT_Z):
            newRow = []
            # Keep values within range bounds, since just adding step can
            # cause minor drift due to the rounding errors.
            z = min(SAMPLE_MAX, (i * stepZ + SAMPLE_MIN))
            for j in range(0, SAMPLE_COUNT_X):
                x = min(SAMPLE_MAX, (j * stepX + SAMPLE_MIN))
                R = sqrt(z * z + x * x) + 0.01
                y = (sin(R) / R + 0.24) * 1.61
                item = QSurfaceDataItem(QVector3D(x, y, z))
                newRow.append(item)
            dataArray.append(newRow)
        self._sqrtSinProxy.resetArray(dataArray)

    @Slot(bool)
    def enableSqrtSinModel(self, enable):
        if enable:
            self._sqrtSinSeries.setDrawMode(QSurface3DSeries.DrawSurfaceAndWireframe)
            self._sqrtSinSeries.setFlatShadingEnabled(True)

            self._graph.axisX().setLabelFormat("%.2f")
            self._graph.axisZ().setLabelFormat("%.2f")
            self._graph.axisX().setRange(SAMPLE_MIN, SAMPLE_MAX)
            self._graph.axisY().setRange(0.0, 2.0)
            self._graph.axisZ().setRange(SAMPLE_MIN, SAMPLE_MAX)
            self._graph.axisX().setLabelAutoRotation(30.0)
            self._graph.axisY().setLabelAutoRotation(90.0)
            self._graph.axisZ().setLabelAutoRotation(30.0)

            self._graph.removeSeries(self._heightMapSeriesOne)
            self._graph.removeSeries(self._heightMapSeriesTwo)
            self._graph.removeSeries(self._heightMapSeriesThree)
            self._graph.removeSeries(self._topography)
            self._graph.removeSeries(self._highlight)

            self._graph.addSeries(self._sqrtSinSeries)

            self._titleLabel.setVisible(False)
            self._graph.axisX().setTitleVisible(False)
            self._graph.axisY().setTitleVisible(False)
            self._graph.axisZ().setTitleVisible(False)

            self._graph.axisX().setTitle("")
            self._graph.axisY().setTitle("")
            self._graph.axisZ().setTitle("")

            self._graph.setActiveInputHandler(self._defaultInputHandler)

            # Reset range sliders for Sqrt & Sin
            self._rangeMinX = SAMPLE_MIN
            self._rangeMinZ = SAMPLE_MIN
            self._stepX = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_X - 1)
            self._stepZ = (SAMPLE_MAX - SAMPLE_MIN) / float(SAMPLE_COUNT_Z - 1)
            self._axisMinSliderX.setMinimum(0)
            self._axisMinSliderX.setMaximum(SAMPLE_COUNT_X - 2)
            self._axisMinSliderX.setValue(0)
            self._axisMaxSliderX.setMinimum(1)
            self._axisMaxSliderX.setMaximum(SAMPLE_COUNT_X - 1)
            self._axisMaxSliderX.setValue(SAMPLE_COUNT_X - 1)
            self._axisMinSliderZ.setMinimum(0)
            self._axisMinSliderZ.setMaximum(SAMPLE_COUNT_Z - 2)
            self._axisMinSliderZ.setValue(0)
            self._axisMaxSliderZ.setMinimum(1)
            self._axisMaxSliderZ.setMaximum(SAMPLE_COUNT_Z - 1)
            self._axisMaxSliderZ.setValue(SAMPLE_COUNT_Z - 1)

    @Slot(bool)
    def enableHeightMapModel(self, enable):
        if enable:
            self._heightMapSeriesOne.setDrawMode(QSurface3DSeries.DrawSurface)
            self._heightMapSeriesOne.setFlatShadingEnabled(False)
            self._heightMapSeriesTwo.setDrawMode(QSurface3DSeries.DrawSurface)
            self._heightMapSeriesTwo.setFlatShadingEnabled(False)
            self._heightMapSeriesThree.setDrawMode(QSurface3DSeries.DrawSurface)
            self._heightMapSeriesThree.setFlatShadingEnabled(False)

            self._graph.axisX().setLabelFormat("%.1f N")
            self._graph.axisZ().setLabelFormat("%.1f E")
            self._graph.axisX().setRange(34.0, 40.0)
            self._graph.axisY().setAutoAdjustRange(True)
            self._graph.axisZ().setRange(18.0, 24.0)

            self._graph.axisX().setTitle("Latitude")
            self._graph.axisY().setTitle("Height")
            self._graph.axisZ().setTitle("Longitude")

            self._graph.removeSeries(self._sqrtSinSeries)
            self._graph.removeSeries(self._topography)
            self._graph.removeSeries(self._highlight)
            self._graph.addSeries(self._heightMapSeriesOne)
            self._graph.addSeries(self._heightMapSeriesTwo)
            self._graph.addSeries(self._heightMapSeriesThree)

            self._graph.setActiveInputHandler(self._defaultInputHandler)

            self._titleLabel.setVisible(True)
            self._graph.axisX().setTitleVisible(True)
            self._graph.axisY().setTitleVisible(True)
            self._graph.axisZ().setTitleVisible(True)

            # Reset range sliders for height map
            mapGridCountX = self._heightMapWidth / HEIGHTMAP_GRID_STEP_X
            mapGridCountZ = self._heightMapHeight / HEIGHTMAP_GRID_STEP_Z
            self._rangeMinX = 34.0
            self._rangeMinZ = 18.0
            self._stepX = 6.0 / float(mapGridCountX - 1)
            self._stepZ = 6.0 / float(mapGridCountZ - 1)
            self._axisMinSliderX.setMinimum(0)
            self._axisMinSliderX.setMaximum(mapGridCountX - 2)
            self._axisMinSliderX.setValue(0)
            self._axisMaxSliderX.setMinimum(1)
            self._axisMaxSliderX.setMaximum(mapGridCountX - 1)
            self._axisMaxSliderX.setValue(mapGridCountX - 1)
            self._axisMinSliderZ.setMinimum(0)
            self._axisMinSliderZ.setMaximum(mapGridCountZ - 2)
            self._axisMinSliderZ.setValue(0)
            self._axisMaxSliderZ.setMinimum(1)
            self._axisMaxSliderZ.setMaximum(mapGridCountZ - 1)
            self._axisMaxSliderZ.setValue(mapGridCountZ - 1)

    @Slot(bool)
    def enableTopographyModel(self, enable):
        if enable:
            self._graph.axisX().setLabelFormat("%i")
            self._graph.axisZ().setLabelFormat("%i")
            self._graph.axisX().setRange(0.0, AREA_WIDTH)
            self._graph.axisY().setRange(100.0, AREA_WIDTH * ASPECT_RATIO)
            self._graph.axisZ().setRange(0.0, AREA_HEIGHT)
            self._graph.axisX().setLabelAutoRotation(30.0)
            self._graph.axisY().setLabelAutoRotation(90.0)
            self._graph.axisZ().setLabelAutoRotation(30.0)

            self._graph.removeSeries(self._heightMapSeriesOne)
            self._graph.removeSeries(self._heightMapSeriesTwo)
            self._graph.removeSeries(self._heightMapSeriesThree)
            self._graph.addSeries(self._topography)
            self._graph.addSeries(self._highlight)

            self._titleLabel.setVisible(False)
            self._graph.axisX().setTitleVisible(False)
            self._graph.axisY().setTitleVisible(False)
            self._graph.axisZ().setTitleVisible(False)

            self._graph.axisX().setTitle("")
            self._graph.axisY().setTitle("")
            self._graph.axisZ().setTitle("")

            self._graph.setActiveInputHandler(self._customInputHandler)

            # Reset range sliders for topography map
            self._rangeMinX = 0.0
            self._rangeMinZ = 0.0
            self._stepX = 1.0
            self._stepZ = 1.0
            self._axisMinSliderX.setMinimum(0)
            self._axisMinSliderX.setMaximum(AREA_WIDTH - 200)
            self._axisMinSliderX.setValue(0)
            self._axisMaxSliderX.setMinimum(200)
            self._axisMaxSliderX.setMaximum(AREA_WIDTH)
            self._axisMaxSliderX.setValue(AREA_WIDTH)
            self._axisMinSliderZ.setMinimum(0)
            self._axisMinSliderZ.setMaximum(AREA_HEIGHT - 200)
            self._axisMinSliderZ.setValue(0)
            self._axisMaxSliderZ.setMinimum(200)
            self._axisMaxSliderZ.setMaximum(AREA_HEIGHT)
            self._axisMaxSliderZ.setValue(AREA_HEIGHT)

    def adjustXMin(self, min):
        minX = self._stepX * float(min) + self._rangeMinX

        max = self._axisMaxSliderX.value()
        if min >= max:
            max = min + 1
            self._axisMaxSliderX.setValue(max)

        maxX = self._stepX * max + self._rangeMinX

        self.setAxisXRange(minX, maxX)

    def adjustXMax(self, max):
        maxX = self._stepX * float(max) + self._rangeMinX

        min = self._axisMinSliderX.value()
        if max <= min:
            min = max - 1
            self._axisMinSliderX.setValue(min)

        minX = self._stepX * min + self._rangeMinX

        self.setAxisXRange(minX, maxX)

    def adjustZMin(self, min):
        minZ = self._stepZ * float(min) + self._rangeMinZ

        max = self._axisMaxSliderZ.value()
        if min >= max:
            max = min + 1
            self._axisMaxSliderZ.setValue(max)

        maxZ = self._stepZ * max + self._rangeMinZ

        self.setAxisZRange(minZ, maxZ)

    def adjustZMax(self, max):
        maxX = self._stepZ * float(max) + self._rangeMinZ

        min = self._axisMinSliderZ.value()
        if max <= min:
            min = max - 1
            self._axisMinSliderZ.setValue(min)

        minX = self._stepZ * min + self._rangeMinZ

        self.setAxisZRange(minX, maxX)

    def setAxisXRange(self, min, max):
        self._graph.axisX().setRange(min, max)

    def setAxisZRange(self, min, max):
        self._graph.axisZ().setRange(min, max)

    def setBlackToYellowGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.black)
        gr.setColorAt(0.33, Qt.blue)
        gr.setColorAt(0.67, Qt.red)
        gr.setColorAt(1.0, Qt.yellow)

        self._sqrtSinSeries.setBaseGradient(gr)
        self._sqrtSinSeries.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    def setGreenToRedGradient(self):
        gr = QLinearGradient()
        gr.setColorAt(0.0, Qt.darkGreen)
        gr.setColorAt(0.5, Qt.yellow)
        gr.setColorAt(0.8, Qt.red)
        gr.setColorAt(1.0, Qt.darkRed)

        self._sqrtSinSeries.setBaseGradient(gr)
        self._sqrtSinSeries.setColorStyle(Q3DTheme.ColorStyleRangeGradient)

    @Slot(bool)
    def toggleItemOne(self, show):
        positionOne = QVector3D(39.0, 77.0, 19.2)
        positionOnePipe = QVector3D(39.0, 45.0, 19.2)
        positionOneLabel = QVector3D(39.0, 107.0, 19.2)
        if show:
            color = QImage(2, 2, QImage.Format_RGB32)
            color.fill(Qt.red)
            file_name = os.fspath(self._data_path / "oilrig.obj")
            item = QCustom3DItem(file_name, positionOne,
                                 QVector3D(0.025, 0.025, 0.025),
                                 QQuaternion.fromAxisAndAngle(0.0, 1.0, 0.0, 45.0),
                                 color)
            self._graph.addCustomItem(item)
            file_name = os.fspath(self._data_path / "pipe.obj")
            item = QCustom3DItem(file_name, positionOnePipe,
                                 QVector3D(0.005, 0.5, 0.005), QQuaternion(),
                                 color)
            item.setShadowCasting(False)
            self._graph.addCustomItem(item)

            label = QCustom3DLabel()
            label.setText("Oil Rig One")
            label.setPosition(positionOneLabel)
            label.setScaling(QVector3D(1.0, 1.0, 1.0))
            self._graph.addCustomItem(label)
        else:
            self.resetSelection()
            self._graph.removeCustomItemAt(positionOne)
            self._graph.removeCustomItemAt(positionOnePipe)
            self._graph.removeCustomItemAt(positionOneLabel)

    @Slot(bool)
    def toggleItemTwo(self, show):
        positionTwo = QVector3D(34.5, 77.0, 23.4)
        positionTwoPipe = QVector3D(34.5, 45.0, 23.4)
        positionTwoLabel = QVector3D(34.5, 107.0, 23.4)
        if show:
            color = QImage(2, 2, QImage.Format_RGB32)
            color.fill(Qt.red)
            item = QCustom3DItem()
            file_name = os.fspath(self._data_path / "oilrig.obj")
            item.setMeshFile(file_name)
            item.setPosition(positionTwo)
            item.setScaling(QVector3D(0.025, 0.025, 0.025))
            item.setRotation(QQuaternion.fromAxisAndAngle(0.0, 1.0, 0.0, 25.0))
            item.setTextureImage(color)
            self._graph.addCustomItem(item)
            file_name = os.fspath(self._data_path / "pipe.obj")
            item = QCustom3DItem(file_name, positionTwoPipe,
                                 QVector3D(0.005, 0.5, 0.005), QQuaternion(),
                                 color)
            item.setShadowCasting(False)
            self._graph.addCustomItem(item)

            label = QCustom3DLabel()
            label.setText("Oil Rig Two")
            label.setPosition(positionTwoLabel)
            label.setScaling(QVector3D(1.0, 1.0, 1.0))
            self._graph.addCustomItem(label)
        else:
            self.resetSelection()
            self._graph.removeCustomItemAt(positionTwo)
            self._graph.removeCustomItemAt(positionTwoPipe)
            self._graph.removeCustomItemAt(positionTwoLabel)

    @Slot(bool)
    def toggleItemThree(self, show):
        positionThree = QVector3D(34.5, 86.0, 19.1)
        positionThreeLabel = QVector3D(34.5, 116.0, 19.1)
        if show:
            color = QImage(2, 2, QImage.Format_RGB32)
            color.fill(Qt.darkMagenta)
            item = QCustom3DItem()
            file_name = os.fspath(self._data_path / "refinery.obj")
            item.setMeshFile(file_name)
            item.setPosition(positionThree)
            item.setScaling(QVector3D(0.04, 0.04, 0.04))
            item.setRotation(QQuaternion.fromAxisAndAngle(0.0, 1.0, 0.0, 75.0))
            item.setTextureImage(color)
            self._graph.addCustomItem(item)

            label = QCustom3DLabel()
            label.setText("Refinery")
            label.setPosition(positionThreeLabel)
            label.setScaling(QVector3D(1.0, 1.0, 1.0))
            self._graph.addCustomItem(label)
        else:
            self.resetSelection()
            self._graph.removeCustomItemAt(positionThree)
            self._graph.removeCustomItemAt(positionThreeLabel)

    @Slot(bool)
    def toggleSeeThrough(self, seethrough):
        s0 = self._graph.seriesList()[0]
        s1 = self._graph.seriesList()[1]
        if seethrough:
            s0.setDrawMode(QSurface3DSeries.DrawWireframe)
            s1.setDrawMode(QSurface3DSeries.DrawWireframe)
        else:
            s0.setDrawMode(QSurface3DSeries.DrawSurface)
            s1.setDrawMode(QSurface3DSeries.DrawSurface)

    @Slot(bool)
    def toggleOilHighlight(self, highlight):
        s2 = self._graph.seriesList()[2]
        if highlight:
            grThree = QLinearGradient()
            grThree.setColorAt(0.0, Qt.black)
            grThree.setColorAt(0.05, Qt.red)
            s2.setBaseGradient(grThree)
        else:
            grThree = QLinearGradient()
            grThree.setColorAt(0.0, Qt.white)
            grThree.setColorAt(0.05, Qt.black)
            s2.setBaseGradient(grThree)

    @Slot(bool)
    def toggleShadows(self, shadows):
        sq = (QAbstract3DGraph.ShadowQualityMedium
              if shadows else QAbstract3DGraph.ShadowQualityNone)
        self._graph.setShadowQuality(sq)

    @Slot(bool)
    def toggleSurfaceTexture(self, enable):
        if enable:
            file_name = os.fspath(self._data_path / "maptexture.jpg")
            self._topography.setTextureFile(file_name)
        else:
            self._topography.setTextureFile("")

    def handleElementSelected(self, type):
        self.resetSelection()
        if type == QAbstract3DGraph.ElementCustomItem:
            item = self._graph.selectedCustomItem()
            text = ""
            if isinstance(item, QCustom3DItem):
                text += "Custom label: "
            else:
                file = item.meshFile().split("/")[-1]
                text += f"{file}: "

            text += str(self._graph.selectedCustomItemIndex())
            self._textField.setText(text)
            self._previouslyAnimatedItem = item
            self._previousScaling = item.scaling()
            self._selectionAnimation.setTargetObject(item)
            self._selectionAnimation.setStartValue(item.scaling())
            self._selectionAnimation.setEndValue(item.scaling() * 1.5)
            self._selectionAnimation.start()
        elif type == QAbstract3DGraph.ElementSeries:
            text = "Surface ("
            series = self._graph.selectedSeries()
            if series:
                point = series.selectedPoint()
                text += f"{point.x()}, {point.y()}"
            text += ")"
            self._textField.setText(text)
        elif (type.value > QAbstract3DGraph.ElementSeries.value
              and type < QAbstract3DGraph.ElementCustomItem.value):
            index = self._graph.selectedLabelIndex()
            text = ""
            if type == QAbstract3DGraph.ElementAxisXLabel:
                text += "Axis X label: "
            elif type == QAbstract3DGraph.ElementAxisYLabel:
                text += "Axis Y label: "
            else:
                text += "Axis Z label: "
            text += str(index)
            self._textField.setText(text)
        else:
            self._textField.setText("Nothing")

    def resetSelection(self):
        self._selectionAnimation.stop()
        if self._previouslyAnimatedItem:
            self._previouslyAnimatedItem.setScaling(self._previousScaling)
        self._previouslyAnimatedItem = None

    def toggleModeNone(self):
        self._graph.setSelectionMode(QAbstract3DGraph.SelectionNone)

    def toggleModeItem(self):
        self._graph.setSelectionMode(QAbstract3DGraph.SelectionItem)

    def toggleModeSliceRow(self):
        sm = (QAbstract3DGraph.SelectionItemAndRow
              | QAbstract3DGraph.SelectionSlice
              | QAbstract3DGraph.SelectionMultiSeries)
        self._graph.setSelectionMode(sm)

    def toggleModeSliceColumn(self):
        sm = (QAbstract3DGraph.SelectionItemAndColumn
              | QAbstract3DGraph.SelectionSlice
              | QAbstract3DGraph.SelectionMultiSeries)
        self._graph.setSelectionMode(sm)

    def setAxisMinSliderX(self, slider):
        self._axisMinSliderX = slider

    def setAxisMaxSliderX(self, slider):
        self._axisMaxSliderX = slider

    def setAxisMinSliderZ(self, slider):
        self._axisMinSliderZ = slider

    def setAxisMaxSliderZ(self, slider):
        self._axisMaxSliderZ = slider
