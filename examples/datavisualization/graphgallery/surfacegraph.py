# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from surfacegraphmodifier import SurfaceGraphModifier

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QBrush, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (QGroupBox, QCheckBox, QLabel, QHBoxLayout,
                               QPushButton, QRadioButton, QSizePolicy, QSlider,
                               QVBoxLayout, QWidget)

from PySide6.QtDataVisualization import (Q3DSurface)


def gradientBtoYPB_Pixmap():
    grBtoY = QLinearGradient(0, 0, 1, 100)
    grBtoY.setColorAt(1.0, Qt.black)
    grBtoY.setColorAt(0.67, Qt.blue)
    grBtoY.setColorAt(0.33, Qt.red)
    grBtoY.setColorAt(0.0, Qt.yellow)
    pm = QPixmap(24, 100)
    with QPainter(pm) as pmp:
        pmp.setBrush(QBrush(grBtoY))
        pmp.setPen(Qt.NoPen)
        pmp.drawRect(0, 0, 24, 100)
    return pm


def gradientGtoRPB_Pixmap():
    grGtoR = QLinearGradient(0, 0, 1, 100)
    grGtoR.setColorAt(1.0, Qt.darkGreen)
    grGtoR.setColorAt(0.5, Qt.yellow)
    grGtoR.setColorAt(0.2, Qt.red)
    grGtoR.setColorAt(0.0, Qt.darkRed)
    pm = QPixmap(24, 100)
    with QPainter(pm) as pmp:
        pmp.setBrush(QBrush(grGtoR))
        pmp.setPen(Qt.NoPen)
        pmp.drawRect(0, 0, 24, 100)
    return pm


def highlightPixmap():
    HEIGHT = 400
    WIDTH = 110
    BORDER = 10
    gr = QLinearGradient(0, 0, 1, HEIGHT - 2 * BORDER)
    gr.setColorAt(1.0, Qt.black)
    gr.setColorAt(0.8, Qt.darkGreen)
    gr.setColorAt(0.6, Qt.green)
    gr.setColorAt(0.4, Qt.yellow)
    gr.setColorAt(0.2, Qt.red)
    gr.setColorAt(0.0, Qt.darkRed)
    pmHighlight = QPixmap(WIDTH, HEIGHT)
    pmHighlight.fill(Qt.transparent)
    with QPainter(pmHighlight) as pmpHighlight:
        pmpHighlight.setBrush(QBrush(gr))
        pmpHighlight.setPen(Qt.NoPen)
        pmpHighlight.drawRect(BORDER, BORDER, 35, HEIGHT - 2 * BORDER)
        pmpHighlight.setPen(Qt.black)
        step = (HEIGHT - 2 * BORDER) / 5
        for i in range(0, 6):
            yPos = i * step + BORDER
            pmpHighlight.drawLine(BORDER, yPos, 55, yPos)
            HEIGHT = 550 - (i * 110)
            pmpHighlight.drawText(60, yPos + 2, f"{HEIGHT} m")
    return pmHighlight


class SurfaceGraph(QObject):

    def __init__(self):
        super().__init__()
        self._surfaceGraph = Q3DSurface()
        self._container = None
        self._surfaceWidget = None

    def initialize(self, minimum_graph_size, maximum_graph_size):
        if not self._surfaceGraph.hasContext():
            return False

        self._surfaceWidget = QWidget()
        hLayout = QHBoxLayout(self._surfaceWidget)
        self._container = QWidget.createWindowContainer(self._surfaceGraph,
                                                        self._surfaceWidget)
        self._container.setMinimumSize(minimum_graph_size)
        self._container.setMaximumSize(maximum_graph_size)
        self._container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._container.setFocusPolicy(Qt.StrongFocus)
        hLayout.addWidget(self._container, 1)
        vLayout = QVBoxLayout()
        hLayout.addLayout(vLayout)
        vLayout.setAlignment(Qt.AlignTop)
        # Create control widgets
        modelGroupBox = QGroupBox("Model")
        sqrtSinModelRB = QRadioButton(self._surfaceWidget)
        sqrtSinModelRB.setText("Sqrt and Sin")
        sqrtSinModelRB.setChecked(False)
        heightMapModelRB = QRadioButton(self._surfaceWidget)
        heightMapModelRB.setText("Multiseries\nHeight Map")
        heightMapModelRB.setChecked(False)
        texturedModelRB = QRadioButton(self._surfaceWidget)
        texturedModelRB.setText("Textured\nTopography")
        texturedModelRB.setChecked(False)
        modelVBox = QVBoxLayout()
        modelVBox.addWidget(sqrtSinModelRB)
        modelVBox.addWidget(heightMapModelRB)
        modelVBox.addWidget(texturedModelRB)
        modelGroupBox.setLayout(modelVBox)
        selectionGroupBox = QGroupBox("Graph Selection Mode")
        modeNoneRB = QRadioButton(self._surfaceWidget)
        modeNoneRB.setText("No selection")
        modeNoneRB.setChecked(False)
        modeItemRB = QRadioButton(self._surfaceWidget)
        modeItemRB.setText("Item")
        modeItemRB.setChecked(False)
        modeSliceRowRB = QRadioButton(self._surfaceWidget)
        modeSliceRowRB.setText("Row Slice")
        modeSliceRowRB.setChecked(False)
        modeSliceColumnRB = QRadioButton(self._surfaceWidget)
        modeSliceColumnRB.setText("Column Slice")
        modeSliceColumnRB.setChecked(False)
        selectionVBox = QVBoxLayout()
        selectionVBox.addWidget(modeNoneRB)
        selectionVBox.addWidget(modeItemRB)
        selectionVBox.addWidget(modeSliceRowRB)
        selectionVBox.addWidget(modeSliceColumnRB)
        selectionGroupBox.setLayout(selectionVBox)
        axisGroupBox = QGroupBox("Axis ranges")
        axisMinSliderX = QSlider(Qt.Orientation.Horizontal)
        axisMinSliderX.setMinimum(0)
        axisMinSliderX.setTickInterval(1)
        axisMinSliderX.setEnabled(True)
        axisMaxSliderX = QSlider(Qt.Orientation.Horizontal)
        axisMaxSliderX.setMinimum(1)
        axisMaxSliderX.setTickInterval(1)
        axisMaxSliderX.setEnabled(True)
        axisMinSliderZ = QSlider(Qt.Orientation.Horizontal)
        axisMinSliderZ.setMinimum(0)
        axisMinSliderZ.setTickInterval(1)
        axisMinSliderZ.setEnabled(True)
        axisMaxSliderZ = QSlider(Qt.Orientation.Horizontal)
        axisMaxSliderZ.setMinimum(1)
        axisMaxSliderZ.setTickInterval(1)
        axisMaxSliderZ.setEnabled(True)
        axisVBox = QVBoxLayout(axisGroupBox)
        axisVBox.addWidget(QLabel("Column range"))
        axisVBox.addWidget(axisMinSliderX)
        axisVBox.addWidget(axisMaxSliderX)
        axisVBox.addWidget(QLabel("Row range"))
        axisVBox.addWidget(axisMinSliderZ)
        axisVBox.addWidget(axisMaxSliderZ)
        # Mode-dependent controls
        # sqrt-sin
        colorGroupBox = QGroupBox("Custom gradient")

        pixmap = gradientBtoYPB_Pixmap()
        gradientBtoYPB = QPushButton(self._surfaceWidget)
        gradientBtoYPB.setIcon(QIcon(pixmap))
        gradientBtoYPB.setIconSize(pixmap.size())

        pixmap = gradientGtoRPB_Pixmap()
        gradientGtoRPB = QPushButton(self._surfaceWidget)
        gradientGtoRPB.setIcon(QIcon(pixmap))
        gradientGtoRPB.setIconSize(pixmap.size())

        colorHBox = QHBoxLayout(colorGroupBox)
        colorHBox.addWidget(gradientBtoYPB)
        colorHBox.addWidget(gradientGtoRPB)
        # Multiseries heightmap
        showGroupBox = QGroupBox("Show Object")
        showGroupBox.setVisible(False)
        checkboxShowOilRigOne = QCheckBox("Oil Rig 1")
        checkboxShowOilRigOne.setChecked(True)
        checkboxShowOilRigTwo = QCheckBox("Oil Rig 2")
        checkboxShowOilRigTwo.setChecked(True)
        checkboxShowRefinery = QCheckBox("Refinery")
        showVBox = QVBoxLayout()
        showVBox.addWidget(checkboxShowOilRigOne)
        showVBox.addWidget(checkboxShowOilRigTwo)
        showVBox.addWidget(checkboxShowRefinery)
        showGroupBox.setLayout(showVBox)
        visualsGroupBox = QGroupBox("Visuals")
        visualsGroupBox.setVisible(False)
        checkboxVisualsSeeThrough = QCheckBox("See-Through")
        checkboxHighlightOil = QCheckBox("Highlight Oil")
        checkboxShowShadows = QCheckBox("Shadows")
        checkboxShowShadows.setChecked(True)
        visualVBox = QVBoxLayout(visualsGroupBox)
        visualVBox.addWidget(checkboxVisualsSeeThrough)
        visualVBox.addWidget(checkboxHighlightOil)
        visualVBox.addWidget(checkboxShowShadows)
        labelSelection = QLabel("Selection:")
        labelSelection.setVisible(False)
        labelSelectedItem = QLabel("Nothing")
        labelSelectedItem.setVisible(False)
        # Textured topography heightmap
        enableTexture = QCheckBox("Surface texture")
        enableTexture.setVisible(False)

        label = QLabel(self._surfaceWidget)
        label.setPixmap(highlightPixmap())
        heightMapGroupBox = QGroupBox("Highlight color map")
        colorMapVBox = QVBoxLayout()
        colorMapVBox.addWidget(label)
        heightMapGroupBox.setLayout(colorMapVBox)
        heightMapGroupBox.setVisible(False)
        # Populate vertical layout
        # Common
        vLayout.addWidget(modelGroupBox)
        vLayout.addWidget(selectionGroupBox)
        vLayout.addWidget(axisGroupBox)
        # Sqrt Sin
        vLayout.addWidget(colorGroupBox)
        # Multiseries heightmap
        vLayout.addWidget(showGroupBox)
        vLayout.addWidget(visualsGroupBox)
        vLayout.addWidget(labelSelection)
        vLayout.addWidget(labelSelectedItem)
        # Textured topography
        vLayout.addWidget(heightMapGroupBox)
        vLayout.addWidget(enableTexture)
        # Create the controller
        modifier = SurfaceGraphModifier(self._surfaceGraph, labelSelectedItem, self)
        # Connect widget controls to controller
        heightMapModelRB.toggled.connect(modifier.enableHeightMapModel)
        sqrtSinModelRB.toggled.connect(modifier.enableSqrtSinModel)
        texturedModelRB.toggled.connect(modifier.enableTopographyModel)
        modeNoneRB.toggled.connect(modifier.toggleModeNone)
        modeItemRB.toggled.connect(modifier.toggleModeItem)
        modeSliceRowRB.toggled.connect(modifier.toggleModeSliceRow)
        modeSliceColumnRB.toggled.connect(modifier.toggleModeSliceColumn)
        axisMinSliderX.valueChanged.connect(modifier.adjustXMin)
        axisMaxSliderX.valueChanged.connect(modifier.adjustXMax)
        axisMinSliderZ.valueChanged.connect(modifier.adjustZMin)
        axisMaxSliderZ.valueChanged.connect(modifier.adjustZMax)
        # Mode dependent connections
        gradientBtoYPB.pressed.connect(modifier.setBlackToYellowGradient)
        gradientGtoRPB.pressed.connect(modifier.setGreenToRedGradient)
        checkboxShowOilRigOne.stateChanged.connect(modifier.toggleItemOne)
        checkboxShowOilRigTwo.stateChanged.connect(modifier.toggleItemTwo)
        checkboxShowRefinery.stateChanged.connect(modifier.toggleItemThree)
        checkboxVisualsSeeThrough.stateChanged.connect(modifier.toggleSeeThrough)
        checkboxHighlightOil.stateChanged.connect(modifier.toggleOilHighlight)
        checkboxShowShadows.stateChanged.connect(modifier.toggleShadows)
        enableTexture.stateChanged.connect(modifier.toggleSurfaceTexture)
        # Connections to disable features depending on mode
        sqrtSinModelRB.toggled.connect(colorGroupBox.setVisible)
        heightMapModelRB.toggled.connect(showGroupBox.setVisible)
        heightMapModelRB.toggled.connect(visualsGroupBox.setVisible)
        heightMapModelRB.toggled.connect(labelSelection.setVisible)
        heightMapModelRB.toggled.connect(labelSelectedItem.setVisible)
        texturedModelRB.toggled.connect(enableTexture.setVisible)
        texturedModelRB.toggled.connect(heightMapGroupBox.setVisible)
        modifier.setAxisMinSliderX(axisMinSliderX)
        modifier.setAxisMaxSliderX(axisMaxSliderX)
        modifier.setAxisMinSliderZ(axisMinSliderZ)
        modifier.setAxisMaxSliderZ(axisMaxSliderZ)
        sqrtSinModelRB.setChecked(True)
        modeItemRB.setChecked(True)
        enableTexture.setChecked(True)
        return True

    def surfaceWidget(self):
        return self._surfaceWidget
