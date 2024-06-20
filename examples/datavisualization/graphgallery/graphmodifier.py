# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations


from math import atan, degrees
import numpy as np

from PySide6.QtCore import QObject, QPropertyAnimation, Signal, Slot
from PySide6.QtGui import QFont, QVector3D
from PySide6.QtDataVisualization import (QAbstract3DGraph, QAbstract3DSeries,
                                         QBarDataItem, QBar3DSeries,
                                         QCategory3DAxis, QValue3DAxis,
                                         Q3DCamera, Q3DTheme)

from rainfalldata import RainfallData

# Set up data
TEMP_OULU = np.array([
    [-7.4, -2.4, 0.0, 3.0, 8.2, 11.6, 14.7, 15.4, 11.4, 4.2, 2.1, -2.3],  # 2015
    [-13.4, -3.9, -1.8, 3.1, 10.6, 13.7, 17.8, 13.6, 10.7, 3.5, -3.1, -4.2],  # 2016
    [-5.7, -6.7, -3.0, -0.1, 4.7, 12.4, 16.1, 14.1, 9.4, 3.0, -0.3, -3.2],  # 2017
    [-6.4, -11.9, -7.4, 1.9, 11.4, 12.4, 21.5, 16.1, 11.0, 4.4, 2.1, -4.1],  # 2018
    [-11.7, -6.1, -2.4, 3.9, 7.2, 14.5, 15.6, 14.4, 8.5, 2.0, -3.0, -1.5],  # 2019
    [-2.1, -3.4, -1.8, 0.6, 7.0, 17.1, 15.6, 15.4, 11.1, 5.6, 1.9, -1.7],  # 2020
    [-9.6, -11.6, -3.2, 2.4, 7.8, 17.3, 19.4, 14.2, 8.0, 5.2, -2.2, -8.6],  # 2021
    [-7.3, -6.4, -1.8, 1.3, 8.1, 15.5, 17.6, 17.6, 9.1, 5.4, -1.5, -4.4]],  # 2022
    np.float64)


TEMP_HELSINKI = np.array([
    [-2.0, -0.1, 1.8, 5.1, 9.7, 13.7, 16.3, 17.3, 12.7, 5.4, 4.6, 2.1],  # 2015
    [-10.3, -0.6, 0.0, 4.9, 14.3, 15.7, 17.7, 16.0, 12.7, 4.6, -1.0, -0.9],  # 2016
    [-2.9, -3.3, 0.7, 2.3, 9.9, 13.8, 16.1, 15.9, 11.4, 5.0, 2.7, 0.7],  # 2017
    [-2.2, -8.4, -4.7, 5.0, 15.3, 15.8, 21.2, 18.2, 13.3, 6.7, 2.8, -2.0],  # 2018
    [-6.2, -0.5, -0.3, 6.8, 10.6, 17.9, 17.5, 16.8, 11.3, 5.2, 1.8, 1.4],  # 2019
    [1.9, 0.5, 1.7, 4.5, 9.5, 18.4, 16.5, 16.8, 13.0, 8.2, 4.4, 0.9],  # 2020
    [-4.7, -8.1, -0.9, 4.5, 10.4, 19.2, 20.9, 15.4, 9.5, 8.0, 1.5, -6.7],  # 2021
    [-3.3, -2.2, -0.2, 3.3, 9.6, 16.9, 18.1, 18.9, 9.2, 7.6, 2.3, -3.4]],  # 2022
    np.float64)


class GraphModifier(QObject):

    shadowQualityChanged = Signal(int)
    backgroundEnabledChanged = Signal(bool)
    gridEnabledChanged = Signal(bool)
    fontChanged = Signal(QFont)
    fontSizeChanged = Signal(int)

    def __init__(self, bargraph, parent):
        super().__init__(parent)
        self._graph = bargraph
        self._temperatureAxis = QValue3DAxis()
        self._yearAxis = QCategory3DAxis()
        self._monthAxis = QCategory3DAxis()
        self._primarySeries = QBar3DSeries()
        self._secondarySeries = QBar3DSeries()
        self._celsiusString = "°C"

        self._xRotation = float(0)
        self._yRotation = float(0)
        self._fontSize = 30
        self._segments = 4
        self._subSegments = 3
        self._minval = float(-20)
        self._maxval = float(20)
        self._barMesh = QAbstract3DSeries.MeshBevelBar
        self._smooth = False
        self._animationCameraX = QPropertyAnimation()
        self._animationCameraY = QPropertyAnimation()
        self._animationCameraZoom = QPropertyAnimation()
        self._animationCameraTarget = QPropertyAnimation()
        self._defaultAngleX = float(0)
        self._defaultAngleY = float(0)
        self._defaultZoom = float(0)
        self._defaultTarget = []
        self._customData = None

        self._graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftMedium)
        theme = self._graph.activeTheme()
        theme.setBackgroundEnabled(False)
        theme.setFont(QFont("Times New Roman", self._fontSize))
        theme.setLabelBackgroundEnabled(True)
        self._graph.setMultiSeriesUniform(True)

        self._months = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November",
                        "December"]
        self._years = ["2015", "2016", "2017", "2018", "2019", "2020",
                       "2021", "2022"]

        self._temperatureAxis.setTitle("Average temperature")
        self._temperatureAxis.setSegmentCount(self._segments)
        self._temperatureAxis.setSubSegmentCount(self._subSegments)
        self._temperatureAxis.setRange(self._minval, self._maxval)
        self._temperatureAxis.setLabelFormat("%.1f " + self._celsiusString)
        self._temperatureAxis.setLabelAutoRotation(30.0)
        self._temperatureAxis.setTitleVisible(True)

        self._yearAxis.setTitle("Year")
        self._yearAxis.setLabelAutoRotation(30.0)
        self._yearAxis.setTitleVisible(True)
        self._monthAxis.setTitle("Month")
        self._monthAxis.setLabelAutoRotation(30.0)
        self._monthAxis.setTitleVisible(True)

        self._graph.setValueAxis(self._temperatureAxis)
        self._graph.setRowAxis(self._yearAxis)
        self._graph.setColumnAxis(self._monthAxis)

        format = "Oulu - @colLabel @rowLabel: @valueLabel"
        self._primarySeries.setItemLabelFormat(format)
        self._primarySeries.setMesh(QAbstract3DSeries.MeshBevelBar)
        self._primarySeries.setMeshSmooth(False)

        format = "Helsinki - @colLabel @rowLabel: @valueLabel"
        self._secondarySeries.setItemLabelFormat(format)
        self._secondarySeries.setMesh(QAbstract3DSeries.MeshBevelBar)
        self._secondarySeries.setMeshSmooth(False)
        self._secondarySeries.setVisible(False)

        self._graph.addSeries(self._primarySeries)
        self._graph.addSeries(self._secondarySeries)

        self.changePresetCamera()

        self.resetTemperatureData()

        # Set up property animations for zooming to the selected bar
        camera = self._graph.scene().activeCamera()
        self._defaultAngleX = camera.xRotation()
        self._defaultAngleY = camera.yRotation()
        self._defaultZoom = camera.zoomLevel()
        self._defaultTarget = camera.target()

        self._animationCameraX.setTargetObject(camera)
        self._animationCameraY.setTargetObject(camera)
        self._animationCameraZoom.setTargetObject(camera)
        self._animationCameraTarget.setTargetObject(camera)

        self._animationCameraX.setPropertyName(b"xRotation")
        self._animationCameraY.setPropertyName(b"yRotation")
        self._animationCameraZoom.setPropertyName(b"zoomLevel")
        self._animationCameraTarget.setPropertyName(b"target")

        duration = 1700
        self._animationCameraX.setDuration(duration)
        self._animationCameraY.setDuration(duration)
        self._animationCameraZoom.setDuration(duration)
        self._animationCameraTarget.setDuration(duration)

        # The zoom always first zooms out above the graph and then zooms in
        zoomOutFraction = 0.3
        self._animationCameraX.setKeyValueAt(zoomOutFraction, 0.0)
        self._animationCameraY.setKeyValueAt(zoomOutFraction, 90.0)
        self._animationCameraZoom.setKeyValueAt(zoomOutFraction, 50.0)
        self._animationCameraTarget.setKeyValueAt(zoomOutFraction,
                                                  QVector3D(0, 0, 0))
        self._customData = RainfallData()

    def resetTemperatureData(self):
        # Create data arrays
        dataSet = []
        dataSet2 = []

        for year in range(0, len(self._years)):
            # Create a data row
            dataRow = []
            dataRow2 = []
            for month in range(0, len(self._months)):
                # Add data to the row
                item = QBarDataItem()
                item.setValue(TEMP_OULU[year][month])
                dataRow.append(item)
                item = QBarDataItem()
                item.setValue(TEMP_HELSINKI[year][month])
                dataRow2.append(item)

            # Add the row to the set
            dataSet.append(dataRow)
            dataSet2.append(dataRow2)

        # Add data to the data proxy (the data proxy assumes ownership of it)
        self._primarySeries.dataProxy().resetArray(dataSet, self._years, self._months)
        self._secondarySeries.dataProxy().resetArray(dataSet2, self._years, self._months)

    @Slot(int)
    def changeRange(self, range):
        if range >= len(self._years):
            self._yearAxis.setRange(0, len(self._years) - 1)
        else:
            self._yearAxis.setRange(range, range)

    @Slot(int)
    def changeStyle(self, style):
        comboBox = self.sender()
        if comboBox:
            self._barMesh = comboBox.itemData(style)
            self._primarySeries.setMesh(self._barMesh)
            self._secondarySeries.setMesh(self._barMesh)
            self._customData.customSeries().setMesh(self._barMesh)

    def changePresetCamera(self):
        self._animationCameraX.stop()
        self._animationCameraY.stop()
        self._animationCameraZoom.stop()
        self._animationCameraTarget.stop()

        # Restore camera target in case animation has changed it
        self._graph.scene().activeCamera().setTarget(QVector3D(0.0, 0.0, 0.0))

        self._preset = Q3DCamera.CameraPresetFront.value

        camera = self._graph.scene().activeCamera()
        camera.setCameraPreset(Q3DCamera.CameraPreset(self._preset))

        self._preset += 1
        if self._preset > Q3DCamera.CameraPresetDirectlyBelow.value:
            self._preset = Q3DCamera.CameraPresetFrontLow.value

    @Slot(int)
    def changeTheme(self, theme):
        currentTheme = self._graph.activeTheme()
        currentTheme.setType(Q3DTheme.Theme(theme))
        self.backgroundEnabledChanged.emit(currentTheme.isBackgroundEnabled())
        self.gridEnabledChanged.emit(currentTheme.isGridEnabled())
        self.fontChanged.emit(currentTheme.font())
        self.fontSizeChanged.emit(currentTheme.font().pointSize())

    def changeLabelBackground(self):
        theme = self._graph.activeTheme()
        theme.setLabelBackgroundEnabled(not theme.isLabelBackgroundEnabled())

    @Slot(int)
    def changeSelectionMode(self, selectionMode):
        comboBox = self.sender()
        if comboBox:
            flags = comboBox.itemData(selectionMode)
            self._graph.setSelectionMode(QAbstract3DGraph.SelectionFlags(flags))

    def changeFont(self, font):
        newFont = font
        self._graph.activeTheme().setFont(newFont)

    def changeFontSize(self, fontsize):
        self._fontSize = fontsize
        font = self._graph.activeTheme().font()
        font.setPointSize(self._fontSize)
        self._graph.activeTheme().setFont(font)

    @Slot(QAbstract3DGraph.ShadowQuality)
    def shadowQualityUpdatedByVisual(self, sq):
        # Updates the UI component to show correct shadow quality
        self.shadowQualityChanged.emit(sq.value)

    @Slot(int)
    def changeLabelRotation(self, rotation):
        self._temperatureAxis.setLabelAutoRotation(float(rotation))
        self._monthAxis.setLabelAutoRotation(float(rotation))
        self._yearAxis.setLabelAutoRotation(float(rotation))

    @Slot(bool)
    def setAxisTitleVisibility(self, enabled):
        self._temperatureAxis.setTitleVisible(enabled)
        self._monthAxis.setTitleVisible(enabled)
        self._yearAxis.setTitleVisible(enabled)

    @Slot(bool)
    def setAxisTitleFixed(self, enabled):
        self._temperatureAxis.setTitleFixed(enabled)
        self._monthAxis.setTitleFixed(enabled)
        self._yearAxis.setTitleFixed(enabled)

    @Slot()
    def zoomToSelectedBar(self):
        self._animationCameraX.stop()
        self._animationCameraY.stop()
        self._animationCameraZoom.stop()
        self._animationCameraTarget.stop()

        camera = self._graph.scene().activeCamera()
        currentX = camera.xRotation()
        currentY = camera.yRotation()
        currentZoom = camera.zoomLevel()
        currentTarget = camera.target()

        self._animationCameraX.setStartValue(currentX)
        self._animationCameraY.setStartValue(currentY)
        self._animationCameraZoom.setStartValue(currentZoom)
        self._animationCameraTarget.setStartValue(currentTarget)

        selectedBar = (self._graph.selectedSeries().selectedBar()
                       if self._graph.selectedSeries()
                       else QBar3DSeries.invalidSelectionPosition())

        if selectedBar != QBar3DSeries.invalidSelectionPosition():
            # Normalize selected bar position within axis range to determine
            # target coordinates
            endTarget = QVector3D()
            xMin = self._graph.columnAxis().min()
            xRange = self._graph.columnAxis().max() - xMin
            zMin = self._graph.rowAxis().min()
            zRange = self._graph.rowAxis().max() - zMin
            endTarget.setX((selectedBar.y() - xMin) / xRange * 2.0 - 1.0)
            endTarget.setZ((selectedBar.x() - zMin) / zRange * 2.0 - 1.0)

            # Rotate the camera so that it always points approximately to the
            # graph center
            endAngleX = 90.0 - degrees(atan(float(endTarget.z() / endTarget.x())))
            if endTarget.x() > 0.0:
                endAngleX -= 180.0
            proxy = self._graph.selectedSeries().dataProxy()
            barValue = proxy.itemAt(selectedBar.x(), selectedBar.y()).value()
            endAngleY = 30.0 if barValue >= 0.0 else -30.0
            if self._graph.valueAxis().reversed():
                endAngleY *= -1.0

            self._animationCameraX.setEndValue(float(endAngleX))
            self._animationCameraY.setEndValue(endAngleY)
            self._animationCameraZoom.setEndValue(250)
            self._animationCameraTarget.setEndValue(endTarget)
        else:
            # No selected bar, so return to the default view
            self._animationCameraX.setEndValue(self._defaultAngleX)
            self._animationCameraY.setEndValue(self._defaultAngleY)
            self._animationCameraZoom.setEndValue(self._defaultZoom)
            self._animationCameraTarget.setEndValue(self._defaultTarget)

        self._animationCameraX.start()
        self._animationCameraY.start()
        self._animationCameraZoom.start()
        self._animationCameraTarget.start()

    @Slot(bool)
    def setDataModeToWeather(self, enabled):
        if enabled:
            self.changeDataMode(False)

    @Slot(bool)
    def setDataModeToCustom(self, enabled):
        if enabled:
            self.changeDataMode(True)

    def changeShadowQuality(self, quality):
        sq = QAbstract3DGraph.ShadowQuality(quality)
        self._graph.setShadowQuality(sq)
        self.shadowQualityChanged.emit(quality)

    def rotateX(self, rotation):
        self._xRotation = rotation
        camera = self._graph.scene().activeCamera()
        camera.setCameraPosition(self._xRotation, self._yRotation)

    def rotateY(self, rotation):
        self._yRotation = rotation
        camera = self._graph.scene().activeCamera()
        camera.setCameraPosition(self._xRotation, self._yRotation)

    def setBackgroundEnabled(self, enabled):
        self._graph.activeTheme().setBackgroundEnabled(bool(enabled))

    def setGridEnabled(self, enabled):
        self._graph.activeTheme().setGridEnabled(bool(enabled))

    def setSmoothBars(self, smooth):
        self._smooth = bool(smooth)
        self._primarySeries.setMeshSmooth(self._smooth)
        self._secondarySeries.setMeshSmooth(self._smooth)
        self._customData.customSeries().setMeshSmooth(self._smooth)

    def setSeriesVisibility(self, enabled):
        self._secondarySeries.setVisible(bool(enabled))

    def setReverseValueAxis(self, enabled):
        self._graph.valueAxis().setReversed(enabled)

    def setReflection(self, enabled):
        self._graph.setReflection(enabled)

    def changeDataMode(self, customData):
        # Change between weather data and data from custom proxy
        if customData:
            self._graph.removeSeries(self._primarySeries)
            self._graph.removeSeries(self._secondarySeries)
            self._graph.addSeries(self._customData.customSeries())
            self._graph.setValueAxis(self._customData.valueAxis())
            self._graph.setRowAxis(self._customData.rowAxis())
            self._graph.setColumnAxis(self._customData.colAxis())
        else:
            self._graph.removeSeries(self._customData.customSeries())
            self._graph.addSeries(self._primarySeries)
            self._graph.addSeries(self._secondarySeries)
            self._graph.setValueAxis(self._temperatureAxis)
            self._graph.setRowAxis(self._yearAxis)
            self._graph.setColumnAxis(self._monthAxis)
