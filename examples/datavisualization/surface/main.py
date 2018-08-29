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

import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtDataVisualization import Q3DSurface
from PySide6.QtGui import QBrush, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
                               QLabel, QMessageBox, QPushButton, QRadioButton,
                               QSizePolicy, QSlider, QVBoxLayout, QWidget)

from surfacegraph import SurfaceGraph

THEMES = ["Qt", "Primary Colors", "Digia", "Stone Moss", "Army Blue", "Retro", "Ebony", "Isabelle"]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    graph = Q3DSurface()
    container = QWidget.createWindowContainer(graph)

    if not graph.hasContext():
        msgBox = QMessageBox()
        msgBox.setText("Couldn't initialize the OpenGL context.")
        msgBox.exec()
        sys.exit(-1)

    screenSize = graph.screen().size()
    container.setMinimumSize(QSize(screenSize.width() / 2, screenSize.height() / 1.6))
    container.setMaximumSize(screenSize)
    container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    container.setFocusPolicy(Qt.StrongFocus)

    widget = QWidget()
    hLayout = QHBoxLayout(widget)
    vLayout = QVBoxLayout()
    hLayout.addWidget(container, 1)
    hLayout.addLayout(vLayout)
    vLayout.setAlignment(Qt.AlignTop)

    widget.setWindowTitle("Surface example")

    modelGroupBox = QGroupBox("Model")

    sqrtSinModelRB = QRadioButton(widget)
    sqrtSinModelRB.setText("Sqrt& Sin")
    sqrtSinModelRB.setChecked(False)

    heightMapModelRB = QRadioButton(widget)
    heightMapModelRB.setText("Height Map")
    heightMapModelRB.setChecked(False)

    modelVBox = QVBoxLayout()
    modelVBox.addWidget(sqrtSinModelRB)
    modelVBox.addWidget(heightMapModelRB)
    modelGroupBox.setLayout(modelVBox)

    selectionGroupBox = QGroupBox("Selection Mode")

    modeNoneRB = QRadioButton(widget)
    modeNoneRB.setText("No selection")
    modeNoneRB.setChecked(False)

    modeItemRB = QRadioButton(widget)
    modeItemRB.setText("Item")
    modeItemRB.setChecked(False)

    modeSliceRowRB = QRadioButton(widget)
    modeSliceRowRB.setText("Row Slice")
    modeSliceRowRB.setChecked(False)

    modeSliceColumnRB = QRadioButton(widget)
    modeSliceColumnRB.setText("Column Slice")
    modeSliceColumnRB.setChecked(False)

    selectionVBox = QVBoxLayout()
    selectionVBox.addWidget(modeNoneRB)
    selectionVBox.addWidget(modeItemRB)
    selectionVBox.addWidget(modeSliceRowRB)
    selectionVBox.addWidget(modeSliceColumnRB)
    selectionGroupBox.setLayout(selectionVBox)

    axisMinSliderX = QSlider(Qt.Horizontal, widget)
    axisMinSliderX.setMinimum(0)
    axisMinSliderX.setTickInterval(1)
    axisMinSliderX.setEnabled(True)
    axisMaxSliderX = QSlider(Qt.Horizontal, widget)
    axisMaxSliderX.setMinimum(1)
    axisMaxSliderX.setTickInterval(1)
    axisMaxSliderX.setEnabled(True)
    axisMinSliderZ = QSlider(Qt.Horizontal, widget)
    axisMinSliderZ.setMinimum(0)
    axisMinSliderZ.setTickInterval(1)
    axisMinSliderZ.setEnabled(True)
    axisMaxSliderZ = QSlider(Qt.Horizontal, widget)
    axisMaxSliderZ.setMinimum(1)
    axisMaxSliderZ.setTickInterval(1)
    axisMaxSliderZ.setEnabled(True)

    themeList = QComboBox(widget)
    themeList.addItems(THEMES)

    colorGroupBox = QGroupBox("Custom gradient")

    grBtoY = QLinearGradient(0, 0, 1, 100)
    grBtoY.setColorAt(1.0, Qt.black)
    grBtoY.setColorAt(0.67, Qt.blue)
    grBtoY.setColorAt(0.33, Qt.red)
    grBtoY.setColorAt(0.0, Qt.yellow)

    pm = QPixmap(24, 100)
    pmp = QPainter(pm)
    pmp.setBrush(QBrush(grBtoY))
    pmp.setPen(Qt.NoPen)
    pmp.drawRect(0, 0, 24, 100)
    pmp.end()

    gradientBtoYPB = QPushButton(widget)
    gradientBtoYPB.setIcon(QIcon(pm))
    gradientBtoYPB.setIconSize(QSize(24, 100))

    grGtoR = QLinearGradient(0, 0, 1, 100)
    grGtoR.setColorAt(1.0, Qt.darkGreen)
    grGtoR.setColorAt(0.5, Qt.yellow)
    grGtoR.setColorAt(0.2, Qt.red)
    grGtoR.setColorAt(0.0, Qt.darkRed)
    pmp.begin(pm)
    pmp.setBrush(QBrush(grGtoR))
    pmp.drawRect(0, 0, 24, 100)
    pmp.end()

    gradientGtoRPB = QPushButton(widget)
    gradientGtoRPB.setIcon(QIcon(pm))
    gradientGtoRPB.setIconSize(QSize(24, 100))

    colorHBox = QHBoxLayout()
    colorHBox.addWidget(gradientBtoYPB)
    colorHBox.addWidget(gradientGtoRPB)
    colorGroupBox.setLayout(colorHBox)

    vLayout.addWidget(modelGroupBox)
    vLayout.addWidget(selectionGroupBox)
    vLayout.addWidget(QLabel("Column range"))
    vLayout.addWidget(axisMinSliderX)
    vLayout.addWidget(axisMaxSliderX)
    vLayout.addWidget(QLabel("Row range"))
    vLayout.addWidget(axisMinSliderZ)
    vLayout.addWidget(axisMaxSliderZ)
    vLayout.addWidget(QLabel("Theme"))
    vLayout.addWidget(themeList)
    vLayout.addWidget(colorGroupBox)

    widget.show()

    modifier = SurfaceGraph(graph)

    heightMapModelRB.toggled.connect(modifier.enableHeightMapModel)
    sqrtSinModelRB.toggled.connect(modifier.enableSqrtSinModel)
    modeNoneRB.toggled.connect(modifier.toggleModeNone)
    modeItemRB.toggled.connect(modifier.toggleModeItem)
    modeSliceRowRB.toggled.connect(modifier.toggleModeSliceRow)
    modeSliceColumnRB.toggled.connect(modifier.toggleModeSliceColumn)
    axisMinSliderX.valueChanged.connect(modifier.adjustXMin)
    axisMaxSliderX.valueChanged.connect(modifier.adjustXMax)
    axisMinSliderZ.valueChanged.connect(modifier.adjustZMin)
    axisMaxSliderZ.valueChanged.connect(modifier.adjustZMax)
    themeList.currentIndexChanged[int].connect(modifier.changeTheme)
    gradientBtoYPB.pressed.connect(modifier.setBlackToYellowGradient)
    gradientGtoRPB.pressed.connect(modifier.setGreenToRedGradient)

    modifier.setAxisMinSliderX(axisMinSliderX)
    modifier.setAxisMaxSliderX(axisMaxSliderX)
    modifier.setAxisMinSliderZ(axisMinSliderZ)
    modifier.setAxisMaxSliderZ(axisMaxSliderZ)

    sqrtSinModelRB.setChecked(True)
    modeItemRB.setChecked(True)
    themeList.setCurrentIndex(2)

    sys.exit(app.exec())
