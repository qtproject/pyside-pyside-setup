# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, QSize, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QCommandLinkButton,
                               QLabel, QHBoxLayout, QSizePolicy,
                               QVBoxLayout, QWidget, )
from PySide6.QtDataVisualization import (QAbstract3DSeries, Q3DScatter)

from scatterdatamodifier import ScatterDataModifier


class ScatterGraph(QObject):

    def __init__(self):
        super().__init__()
        self._scatterGraph = Q3DScatter()
        self._container = None
        self._scatterWidget = None

    def initialize(self, minimum_graph_size, maximum_graph_size):
        if not self._scatterGraph.hasContext():
            return -1

        self._scatterWidget = QWidget()
        hLayout = QHBoxLayout(self._scatterWidget)
        self._container = QWidget.createWindowContainer(self._scatterGraph, self._scatterWidget)
        self._container.setMinimumSize(minimum_graph_size)
        self._container.setMaximumSize(maximum_graph_size)
        self._container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._container.setFocusPolicy(Qt.StrongFocus)
        hLayout.addWidget(self._container, 1)

        vLayout = QVBoxLayout()
        hLayout.addLayout(vLayout)

        cameraButton = QCommandLinkButton(self._scatterWidget)
        cameraButton.setText("Change camera preset")
        cameraButton.setDescription("Switch between a number of preset camera positions")
        cameraButton.setIconSize(QSize(0, 0))

        itemCountButton = QCommandLinkButton(self._scatterWidget)
        itemCountButton.setText("Toggle item count")
        itemCountButton.setDescription("Switch between 900 and 10000 data points")
        itemCountButton.setIconSize(QSize(0, 0))

        rangeButton = QCommandLinkButton(self._scatterWidget)
        rangeButton.setText("Toggle axis ranges")
        rangeButton.setDescription("Switch between automatic axis ranges and preset ranges")
        rangeButton.setIconSize(QSize(0, 0))

        backgroundCheckBox = QCheckBox(self._scatterWidget)
        backgroundCheckBox.setText("Show background")
        backgroundCheckBox.setChecked(True)

        gridCheckBox = QCheckBox(self._scatterWidget)
        gridCheckBox.setText("Show grid")
        gridCheckBox.setChecked(True)

        smoothCheckBox = QCheckBox(self._scatterWidget)
        smoothCheckBox.setText("Smooth dots")
        smoothCheckBox.setChecked(True)

        itemStyleList = QComboBox(self._scatterWidget)
        itemStyleList.addItem("Sphere", QAbstract3DSeries.MeshSphere)
        itemStyleList.addItem("Cube", QAbstract3DSeries.MeshCube)
        itemStyleList.addItem("Minimal", QAbstract3DSeries.MeshMinimal)
        itemStyleList.addItem("Point", QAbstract3DSeries.MeshPoint)
        itemStyleList.setCurrentIndex(0)

        themeList = QComboBox(self._scatterWidget)
        themeList.addItem("Qt")
        themeList.addItem("Primary Colors")
        themeList.addItem("Digia")
        themeList.addItem("Stone Moss")
        themeList.addItem("Army Blue")
        themeList.addItem("Retro")
        themeList.addItem("Ebony")
        themeList.addItem("Isabelle")
        themeList.setCurrentIndex(3)

        shadowQuality = QComboBox(self._scatterWidget)
        shadowQuality.addItem("None")
        shadowQuality.addItem("Low")
        shadowQuality.addItem("Medium")
        shadowQuality.addItem("High")
        shadowQuality.addItem("Low Soft")
        shadowQuality.addItem("Medium Soft")
        shadowQuality.addItem("High Soft")
        shadowQuality.setCurrentIndex(6)

        vLayout.addWidget(cameraButton)
        vLayout.addWidget(itemCountButton)
        vLayout.addWidget(rangeButton)
        vLayout.addWidget(backgroundCheckBox)
        vLayout.addWidget(gridCheckBox)
        vLayout.addWidget(smoothCheckBox)
        vLayout.addWidget(QLabel("Change dot style"))
        vLayout.addWidget(itemStyleList)
        vLayout.addWidget(QLabel("Change theme"))
        vLayout.addWidget(themeList)
        vLayout.addWidget(QLabel("Adjust shadow quality"))
        vLayout.addWidget(shadowQuality, 1, Qt.AlignTop)

        self._modifier = ScatterDataModifier(self._scatterGraph, self)

        cameraButton.clicked.connect(self._modifier.changePresetCamera)
        itemCountButton.clicked.connect(self._modifier.toggleItemCount)
        rangeButton.clicked.connect(self._modifier.toggleRanges)

        backgroundCheckBox.stateChanged.connect(self._modifier.setBackgroundEnabled)
        gridCheckBox.stateChanged.connect(self._modifier.setGridEnabled)
        smoothCheckBox.stateChanged.connect(self._modifier.setSmoothDots)

        self._modifier.backgroundEnabledChanged.connect(backgroundCheckBox.setChecked)
        self._modifier.gridEnabledChanged.connect(gridCheckBox.setChecked)
        itemStyleList.currentIndexChanged.connect(self._modifier.changeStyle)

        themeList.currentIndexChanged.connect(self._modifier.changeTheme)

        shadowQuality.currentIndexChanged.connect(self._modifier.changeShadowQuality)

        self._modifier.shadowQualityChanged.connect(shadowQuality.setCurrentIndex)
        self._scatterGraph.shadowQualityChanged.connect(self._modifier.shadowQualityUpdatedByVisual)
        return True

    def scatterWidget(self):
        return self._scatterWidget
