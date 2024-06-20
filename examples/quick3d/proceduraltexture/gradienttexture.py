# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Signal, Property, QSize
from PySide6.QtGui import QColor
from PySide6.QtQuick3D import QQuick3DTextureData
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "ProceduralTextureModule"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class GradientTexture(QQuick3DTextureData):

    heightChanged = Signal(int)
    widthChanged = Signal(int)
    startColorChanged = Signal(QColor)
    endColorChanged = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._height = 256
        self._width = 256
        self._startcolor = QColor("#d4fc79")
        self._endcolor = QColor("#96e6a1")
        self.updateTexture()

    @Property(int, notify=heightChanged)
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        if self._height == val:
            return
        self._height = val
        self.updateTexture()
        self.heightChanged.emit(self._height)

    @Property(int, notify=widthChanged)
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        if self._width == val:
            return
        self._width = val
        self.updateTexture()
        self.widthChanged.emit(self._width)

    @Property(QColor, notify=startColorChanged)
    def startColor(self):
        return self._startcolor

    @startColor.setter
    def startColor(self, val):
        if self._startcolor == val:
            return
        self._startcolor = val
        self.updateTexture()
        self.startColorChanged.emit(self._startcolor)

    @Property(QColor, notify=endColorChanged)
    def endColor(self):
        return self._endcolor

    @endColor.setter
    def endColor(self, val):
        if self._endcolor == val:
            return
        self._endcolor = val
        self.updateTexture()
        self.endColorChanged.emit(self._endcolor)

    def updateTexture(self):
        self.setSize(QSize(self._width, self._height))
        self.setFormat(QQuick3DTextureData.RGBA8)
        self.setHasTransparency(False)
        self.setTextureData(self.generate_texture())

    def generate_texture(self):
        # Generate a horizontal gradient by interpolating between start and end colors.
        gradientScanline = [
            self.linear_interpolate(self._startcolor, self._endcolor, x / self._width)
            for x in range(self._width)
        ]
        # Convert the gradient colors to a flattened list of RGBA values.
        flattenedGradient = [
            component
            for color in gradientScanline
            for component in (color.red(), color.green(), color.blue(), 255)
        ]
        # Repeat the gradient vertically to form the texture.
        return bytearray(flattenedGradient * self._height)

    def linear_interpolate(self, color1, color2, value):
        output = QColor()

        output.setRedF(color1.redF() + (value * (color2.redF() - color1.redF())))
        output.setGreenF(color1.greenF() + (value * (color2.greenF() - color1.greenF())))
        output.setBlueF(color1.blueF() + (value * (color2.blueF() - color1.blueF())))

        return output
