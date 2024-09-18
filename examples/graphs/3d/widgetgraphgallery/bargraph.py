# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from graphmodifier import GraphModifier

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QFontComboBox,
                               QLabel, QPushButton, QHBoxLayout, QSizePolicy,
                               QRadioButton, QSlider, QVBoxLayout, QWidget)
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtGraphs import QAbstract3DSeries, QtGraphs3D
from PySide6.QtGraphsWidgets import Q3DBarsWidgetItem


class BarGraph(QObject):

    def __init__(self, minimum_graph_size, maximum_graph_size):
        super().__init__()

        barsGraph = Q3DBarsWidgetItem()
        barsGraphWidget = QQuickWidget()
        barsGraph.setWidget(barsGraphWidget)
        self._barsWidget = QWidget()
        hLayout = QHBoxLayout(self._barsWidget)
        barsGraphWidget.setMinimumSize(minimum_graph_size)
        barsGraphWidget.setMaximumSize(maximum_graph_size)
        barsGraphWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        barsGraphWidget.setFocusPolicy(Qt.StrongFocus)
        hLayout.addWidget(barsGraphWidget, 1)

        vLayout = QVBoxLayout()
        hLayout.addLayout(vLayout)

        themeList = QComboBox(self._barsWidget)
        themeList.addItem("QtGreen")
        themeList.addItem("QtGreenNeon")
        themeList.addItem("MixSeries")
        themeList.addItem("OrangeSeries")
        themeList.addItem("YellowSeries")
        themeList.addItem("BlueSeries")
        themeList.addItem("PurpleSeries")
        themeList.addItem("GreySeries")
        themeList.setCurrentIndex(0)

        labelButton = QPushButton(self._barsWidget)
        labelButton.setText("Change label style")

        smoothCheckBox = QCheckBox(self._barsWidget)
        smoothCheckBox.setText("Smooth bars")
        smoothCheckBox.setChecked(False)

        barStyleList = QComboBox(self._barsWidget)
        barStyleList.addItem("Bar", QAbstract3DSeries.Mesh.Bar)
        barStyleList.addItem("Pyramid", QAbstract3DSeries.Mesh.Pyramid)
        barStyleList.addItem("Cone", QAbstract3DSeries.Mesh.Cone)
        barStyleList.addItem("Cylinder", QAbstract3DSeries.Mesh.Cylinder)
        barStyleList.addItem("Bevel bar", QAbstract3DSeries.Mesh.BevelBar)
        barStyleList.addItem("Sphere", QAbstract3DSeries.Mesh.Sphere)
        barStyleList.setCurrentIndex(4)

        cameraButton = QPushButton(self._barsWidget)
        cameraButton.setText("Change camera preset")

        zoomToSelectedButton = QPushButton(self._barsWidget)
        zoomToSelectedButton.setText("Zoom to selected bar")

        selectionModeList = QComboBox(self._barsWidget)
        selectionModeList.addItem("None", QtGraphs3D.SelectionFlag.None_)
        selectionModeList.addItem("Bar", QtGraphs3D.SelectionFlag.Item)
        selectionModeList.addItem("Row", QtGraphs3D.SelectionFlag.Row)
        sel = QtGraphs3D.SelectionFlag.ItemAndRow
        selectionModeList.addItem("Bar and Row", sel)
        selectionModeList.addItem("Column", QtGraphs3D.SelectionFlag.Column)
        sel = QtGraphs3D.SelectionFlag.ItemAndColumn
        selectionModeList.addItem("Bar and Column", sel)
        sel = QtGraphs3D.SelectionFlag.RowAndColumn
        selectionModeList.addItem("Row and Column", sel)
        sel = QtGraphs3D.SelectionFlag.RowAndColumn
        selectionModeList.addItem("Bar, Row and Column", sel)
        sel = QtGraphs3D.SelectionFlag.Slice | QtGraphs3D.SelectionFlag.Row
        selectionModeList.addItem("Slice into Row", sel)
        sel = QtGraphs3D.SelectionFlag.Slice | QtGraphs3D.SelectionFlag.ItemAndRow
        selectionModeList.addItem("Slice into Row and Item", sel)
        sel = QtGraphs3D.SelectionFlag.Slice | QtGraphs3D.SelectionFlag.Column
        selectionModeList.addItem("Slice into Column", sel)
        sel = (QtGraphs3D.SelectionFlag.Slice
               | QtGraphs3D.SelectionFlag.ItemAndColumn)
        selectionModeList.addItem("Slice into Column and Item", sel)
        sel = (QtGraphs3D.SelectionFlag.ItemRowAndColumn
               | QtGraphs3D.SelectionFlag.MultiSeries)
        selectionModeList.addItem("Multi: Bar, Row, Col", sel)
        sel = (QtGraphs3D.SelectionFlag.Slice
               | QtGraphs3D.SelectionFlag.ItemAndRow
               | QtGraphs3D.SelectionFlag.MultiSeries)
        selectionModeList.addItem("Multi, Slice: Row, Item", sel)
        sel = (QtGraphs3D.SelectionFlag.Slice
               | QtGraphs3D.SelectionFlag.ItemAndColumn
               | QtGraphs3D.SelectionFlag.MultiSeries)
        selectionModeList.addItem("Multi, Slice: Col, Item", sel)
        selectionModeList.setCurrentIndex(1)

        backgroundCheckBox = QCheckBox(self._barsWidget)
        backgroundCheckBox.setText("Show background")
        backgroundCheckBox.setChecked(False)

        gridCheckBox = QCheckBox(self._barsWidget)
        gridCheckBox.setText("Show grid")
        gridCheckBox.setChecked(True)

        seriesCheckBox = QCheckBox(self._barsWidget)
        seriesCheckBox.setText("Show second series")
        seriesCheckBox.setChecked(False)

        reverseValueAxisCheckBox = QCheckBox(self._barsWidget)
        reverseValueAxisCheckBox.setText("Reverse value axis")
        reverseValueAxisCheckBox.setChecked(False)

        rotationSliderX = QSlider(Qt.Orientation.Horizontal, self._barsWidget)
        rotationSliderX.setTickInterval(30)
        rotationSliderX.setTickPosition(QSlider.TicksBelow)
        rotationSliderX.setMinimum(-180)
        rotationSliderX.setValue(0)
        rotationSliderX.setMaximum(180)
        rotationSliderY = QSlider(Qt.Orientation.Horizontal, self._barsWidget)
        rotationSliderY.setTickInterval(15)
        rotationSliderY.setTickPosition(QSlider.TicksAbove)
        rotationSliderY.setMinimum(-90)
        rotationSliderY.setValue(0)
        rotationSliderY.setMaximum(90)

        fontSizeSlider = QSlider(Qt.Orientation.Horizontal, self._barsWidget)
        fontSizeSlider.setTickInterval(10)
        fontSizeSlider.setTickPosition(QSlider.TicksBelow)
        fontSizeSlider.setMinimum(1)
        fontSizeSlider.setValue(30)
        fontSizeSlider.setMaximum(100)

        fontList = QFontComboBox(self._barsWidget)
        fontList.setCurrentFont(QFont("Times New Roman"))

        shadowQuality = QComboBox(self._barsWidget)
        shadowQuality.addItem("None")
        shadowQuality.addItem("Low")
        shadowQuality.addItem("Medium")
        shadowQuality.addItem("High")
        shadowQuality.addItem("Low Soft")
        shadowQuality.addItem("Medium Soft")
        shadowQuality.addItem("High Soft")
        shadowQuality.setCurrentIndex(5)

        rangeList = QComboBox(self._barsWidget)
        rangeList.addItem("2015")
        rangeList.addItem("2016")
        rangeList.addItem("2017")
        rangeList.addItem("2018")
        rangeList.addItem("2019")
        rangeList.addItem("2020")
        rangeList.addItem("2021")
        rangeList.addItem("2022")
        rangeList.addItem("All")
        rangeList.setCurrentIndex(8)

        axisTitlesVisibleCB = QCheckBox(self._barsWidget)
        axisTitlesVisibleCB.setText("Axis titles visible")
        axisTitlesVisibleCB.setChecked(True)

        axisTitlesFixedCB = QCheckBox(self._barsWidget)
        axisTitlesFixedCB.setText("Axis titles fixed")
        axisTitlesFixedCB.setChecked(True)

        axisLabelRotationSlider = QSlider(Qt.Orientation.Horizontal, self._barsWidget)
        axisLabelRotationSlider.setTickInterval(10)
        axisLabelRotationSlider.setTickPosition(QSlider.TicksBelow)
        axisLabelRotationSlider.setMinimum(0)
        axisLabelRotationSlider.setValue(30)
        axisLabelRotationSlider.setMaximum(90)

        modeGroup = QButtonGroup(self._barsWidget)
        modeWeather = QRadioButton("Temperature Data", self._barsWidget)
        modeWeather.setChecked(True)
        modeCustomProxy = QRadioButton("Custom Proxy Data", self._barsWidget)
        modeGroup.addButton(modeWeather)
        modeGroup.addButton(modeCustomProxy)

        vLayout.addWidget(QLabel("Rotate horizontally"))
        vLayout.addWidget(rotationSliderX, 0, Qt.AlignTop)
        vLayout.addWidget(QLabel("Rotate vertically"))
        vLayout.addWidget(rotationSliderY, 0, Qt.AlignTop)
        vLayout.addWidget(labelButton, 0, Qt.AlignTop)
        vLayout.addWidget(cameraButton, 0, Qt.AlignTop)
        vLayout.addWidget(zoomToSelectedButton, 0, Qt.AlignTop)
        vLayout.addWidget(backgroundCheckBox)
        vLayout.addWidget(gridCheckBox)
        vLayout.addWidget(smoothCheckBox)
        vLayout.addWidget(seriesCheckBox)
        vLayout.addWidget(reverseValueAxisCheckBox)
        vLayout.addWidget(axisTitlesVisibleCB)
        vLayout.addWidget(axisTitlesFixedCB)
        vLayout.addWidget(QLabel("Show year"))
        vLayout.addWidget(rangeList)
        vLayout.addWidget(QLabel("Change bar style"))
        vLayout.addWidget(barStyleList)
        vLayout.addWidget(QLabel("Change selection mode"))
        vLayout.addWidget(selectionModeList)
        vLayout.addWidget(QLabel("Change theme"))
        vLayout.addWidget(themeList)
        vLayout.addWidget(QLabel("Adjust shadow quality"))
        vLayout.addWidget(shadowQuality)
        vLayout.addWidget(QLabel("Change font"))
        vLayout.addWidget(fontList)
        vLayout.addWidget(QLabel("Adjust font size"))
        vLayout.addWidget(fontSizeSlider)
        vLayout.addWidget(QLabel("Axis label rotation"))
        vLayout.addWidget(axisLabelRotationSlider, 0, Qt.AlignTop)
        vLayout.addWidget(modeWeather, 0, Qt.AlignTop)
        vLayout.addWidget(modeCustomProxy, 1, Qt.AlignTop)

        modifier = GraphModifier(barsGraph, self)
        modifier.changeTheme(themeList.currentIndex())

        rotationSliderX.valueChanged.connect(modifier.rotateX)
        rotationSliderY.valueChanged.connect(modifier.rotateY)

        labelButton.clicked.connect(modifier.changeLabelBackground)
        cameraButton.clicked.connect(modifier.changePresetCamera)
        zoomToSelectedButton.clicked.connect(modifier.zoomToSelectedBar)

        backgroundCheckBox.checkStateChanged.connect(modifier.setPlotAreaBackgroundVisible)
        gridCheckBox.checkStateChanged.connect(modifier.setGridVisible)
        smoothCheckBox.checkStateChanged.connect(modifier.setSmoothBars)
        seriesCheckBox.checkStateChanged.connect(modifier.setSeriesVisibility)
        reverseValueAxisCheckBox.checkStateChanged.connect(modifier.setReverseValueAxis)

        modifier.backgroundVisibleChanged.connect(backgroundCheckBox.setChecked)
        modifier.gridVisibleChanged.connect(gridCheckBox.setChecked)

        rangeList.currentIndexChanged.connect(modifier.changeRange)

        barStyleList.currentIndexChanged.connect(modifier.changeStyle)

        selectionModeList.currentIndexChanged.connect(modifier.changeSelectionMode)

        themeList.currentIndexChanged.connect(modifier.changeTheme)

        shadowQuality.currentIndexChanged.connect(modifier.changeShadowQuality)

        modifier.shadowQualityChanged.connect(shadowQuality.setCurrentIndex)
        barsGraph.shadowQualityChanged.connect(modifier.shadowQualityUpdatedByVisual)

        fontSizeSlider.valueChanged.connect(modifier.changeFontSize)
        fontList.currentFontChanged.connect(modifier.changeFont)

        modifier.fontSizeChanged.connect(fontSizeSlider.setValue)
        modifier.fontChanged.connect(fontList.setCurrentFont)

        axisTitlesVisibleCB.checkStateChanged.connect(modifier.setAxisTitleVisibility)
        axisTitlesFixedCB.checkStateChanged.connect(modifier.setAxisTitleFixed)
        axisLabelRotationSlider.valueChanged.connect(modifier.changeLabelRotation)

        modeWeather.toggled.connect(modifier.setDataModeToWeather)
        modeCustomProxy.toggled.connect(modifier.setDataModeToCustom)
        modeWeather.toggled.connect(seriesCheckBox.setEnabled)
        modeWeather.toggled.connect(rangeList.setEnabled)
        modeWeather.toggled.connect(axisTitlesVisibleCB.setEnabled)
        modeWeather.toggled.connect(axisTitlesFixedCB.setEnabled)
        modeWeather.toggled.connect(axisLabelRotationSlider.setEnabled)

    def barsWidget(self):
        return self._barsWidget
