# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from graphmodifier import GraphModifier

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QFontComboBox,
                               QLabel, QPushButton, QHBoxLayout, QSizePolicy,
                               QRadioButton, QSlider, QVBoxLayout, QWidget)
from PySide6.QtDataVisualization import (QAbstract3DGraph, QAbstract3DSeries, Q3DBars)


class BarGraph(QObject):

    def __init__(self):
        super().__init__()
        self._barsGraph = Q3DBars()
        self._container = None
        self._barsWidget = None

    def barsWidget(self):
        return self._barsWidget

    def initialize(self, minimum_graph_size, maximum_graph_size):
        if not self._barsGraph.hasContext():
            return False

        self._barsWidget = QWidget()
        hLayout = QHBoxLayout(self._barsWidget)
        self._container = QWidget.createWindowContainer(self._barsGraph,
                                                        self._barsWidget)
        self._container.setMinimumSize(minimum_graph_size)
        self._container.setMaximumSize(maximum_graph_size)
        self._container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._container.setFocusPolicy(Qt.StrongFocus)
        hLayout.addWidget(self._container, 1)

        vLayout = QVBoxLayout()
        hLayout.addLayout(vLayout)

        themeList = QComboBox(self._barsWidget)
        themeList.addItem("Qt")
        themeList.addItem("Primary Colors")
        themeList.addItem("Digia")
        themeList.addItem("Stone Moss")
        themeList.addItem("Army Blue")
        themeList.addItem("Retro")
        themeList.addItem("Ebony")
        themeList.addItem("Isabelle")
        themeList.setCurrentIndex(0)

        labelButton = QPushButton(self._barsWidget)
        labelButton.setText("Change label style")

        smoothCheckBox = QCheckBox(self._barsWidget)
        smoothCheckBox.setText("Smooth bars")
        smoothCheckBox.setChecked(False)

        barStyleList = QComboBox(self._barsWidget)
        barStyleList.addItem("Bar", QAbstract3DSeries.MeshBar)
        barStyleList.addItem("Pyramid", QAbstract3DSeries.MeshPyramid)
        barStyleList.addItem("Cone", QAbstract3DSeries.MeshCone)
        barStyleList.addItem("Cylinder", QAbstract3DSeries.MeshCylinder)
        barStyleList.addItem("Bevel bar", QAbstract3DSeries.MeshBevelBar)
        barStyleList.addItem("Sphere", QAbstract3DSeries.MeshSphere)
        barStyleList.setCurrentIndex(4)

        cameraButton = QPushButton(self._barsWidget)
        cameraButton.setText("Change camera preset")

        zoomToSelectedButton = QPushButton(self._barsWidget)
        zoomToSelectedButton.setText("Zoom to selected bar")

        selectionModeList = QComboBox(self._barsWidget)
        selectionModeList.addItem("None", QAbstract3DGraph.SelectionNone)
        selectionModeList.addItem("Bar", QAbstract3DGraph.SelectionItem)
        selectionModeList.addItem("Row", QAbstract3DGraph.SelectionRow)
        sel = QAbstract3DGraph.SelectionItemAndRow
        selectionModeList.addItem("Bar and Row", sel)
        selectionModeList.addItem("Column", QAbstract3DGraph.SelectionColumn)
        sel = QAbstract3DGraph.SelectionItemAndColumn
        selectionModeList.addItem("Bar and Column", sel)
        sel = QAbstract3DGraph.SelectionRowAndColumn
        selectionModeList.addItem("Row and Column", sel)
        sel = QAbstract3DGraph.SelectionItemRowAndColumn
        selectionModeList.addItem("Bar, Row and Column", sel)
        sel = QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionRow
        selectionModeList.addItem("Slice into Row", sel)
        sel = QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndRow
        selectionModeList.addItem("Slice into Row and Item", sel)
        sel = QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionColumn
        selectionModeList.addItem("Slice into Column", sel)
        sel = (QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndColumn)
        selectionModeList.addItem("Slice into Column and Item", sel)
        sel = (QAbstract3DGraph.SelectionItemRowAndColumn | QAbstract3DGraph.SelectionMultiSeries)
        selectionModeList.addItem("Multi: Bar, Row, Col", sel)
        sel = (QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndRow
               | QAbstract3DGraph.SelectionMultiSeries)
        selectionModeList.addItem("Multi, Slice: Row, Item", sel)
        sel = (QAbstract3DGraph.SelectionSlice | QAbstract3DGraph.SelectionItemAndColumn
               | QAbstract3DGraph.SelectionMultiSeries)
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

        reflectionCheckBox = QCheckBox(self._barsWidget)
        reflectionCheckBox.setText("Show reflections")
        reflectionCheckBox.setChecked(False)

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
        vLayout.addWidget(reflectionCheckBox)
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

        self._modifier = GraphModifier(self._barsGraph, self)

        rotationSliderX.valueChanged.connect(self._modifier.rotateX)
        rotationSliderY.valueChanged.connect(self._modifier.rotateY)

        labelButton.clicked.connect(self._modifier.changeLabelBackground)
        cameraButton.clicked.connect(self._modifier.changePresetCamera)
        zoomToSelectedButton.clicked.connect(self._modifier.zoomToSelectedBar)

        backgroundCheckBox.stateChanged.connect(self._modifier.setBackgroundEnabled)
        gridCheckBox.stateChanged.connect(self._modifier.setGridEnabled)
        smoothCheckBox.stateChanged.connect(self._modifier.setSmoothBars)
        seriesCheckBox.stateChanged.connect(self._modifier.setSeriesVisibility)
        reverseValueAxisCheckBox.stateChanged.connect(self._modifier.setReverseValueAxis)
        reflectionCheckBox.stateChanged.connect(self._modifier.setReflection)

        self._modifier.backgroundEnabledChanged.connect(backgroundCheckBox.setChecked)
        self._modifier.gridEnabledChanged.connect(gridCheckBox.setChecked)

        rangeList.currentIndexChanged.connect(self._modifier.changeRange)

        barStyleList.currentIndexChanged.connect(self._modifier.changeStyle)

        selectionModeList.currentIndexChanged.connect(self._modifier.changeSelectionMode)

        themeList.currentIndexChanged.connect(self._modifier.changeTheme)

        shadowQuality.currentIndexChanged.connect(self._modifier.changeShadowQuality)

        self._modifier.shadowQualityChanged.connect(shadowQuality.setCurrentIndex)
        self._barsGraph.shadowQualityChanged.connect(self._modifier.shadowQualityUpdatedByVisual)

        fontSizeSlider.valueChanged.connect(self._modifier.changeFontSize)
        fontList.currentFontChanged.connect(self._modifier.changeFont)

        self._modifier.fontSizeChanged.connect(fontSizeSlider.setValue)
        self._modifier.fontChanged.connect(fontList.setCurrentFont)

        axisTitlesVisibleCB.stateChanged.connect(self._modifier.setAxisTitleVisibility)
        axisTitlesFixedCB.stateChanged.connect(self._modifier.setAxisTitleFixed)
        axisLabelRotationSlider.valueChanged.connect(self._modifier.changeLabelRotation)

        modeWeather.toggled.connect(self._modifier.setDataModeToWeather)
        modeCustomProxy.toggled.connect(self._modifier.setDataModeToCustom)
        modeWeather.toggled.connect(seriesCheckBox.setEnabled)
        modeWeather.toggled.connect(rangeList.setEnabled)
        modeWeather.toggled.connect(axisTitlesVisibleCB.setEnabled)
        modeWeather.toggled.connect(axisTitlesFixedCB.setEnabled)
        modeWeather.toggled.connect(axisLabelRotationSlider.setEnabled)
        return True
