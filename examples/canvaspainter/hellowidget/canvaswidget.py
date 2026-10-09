# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCanvasPainter import (QCanvasPainter, QCanvasPainterWidget,
                                     QCanvasImagePattern, QCanvasRadialGradient)
from PySide6.QtGui import QColor, QFont, QImage
from PySide6.QtCore import QPointF, Qt

import rc_hellowidget  # noqa F401


class CanvasWidget(QCanvasPainterWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_image = None
        self.setFillColor(Qt.GlobalColor.white)

    def initializeResources(self, p):
        assert (self.m_image is None)
        flags = QCanvasPainter.ImageFlag.Repeat | QCanvasPainter.ImageFlag.GenerateMipmaps
        image = QImage(":/qt-translucent.png")
        assert (not image.size().isEmpty())
        self.m_image = p.addImage(image, flags)

    def graphicsResourcesInvalidated(self):
        self.m_image = None

    def paint(self, p):
        size = min(self.width(), self.height())
        centerX = self.width() / 2
        centerY = self.height() / 2

        # Paint the background circle
        gradient1 = QCanvasRadialGradient(centerX, centerY - size * 0.1, 0, size * 0.6)
        gradient1.setStartColor(QColor(0x909090))
        gradient1.setEndColor(QColor(0x404040))
        p.beginPath()
        p.circle(QPointF(centerX, centerY), size * 0.46)
        p.setFillStyle(gradient1)
        p.fill()
        p.setStrokeStyle(QColor(0x202020))
        p.setLineWidth(size * 0.02)
        p.stroke()
        # Hello text
        p.setTextAlign(QCanvasPainter.TextAlign.Center)
        p.setTextBaseline(QCanvasPainter.TextBaseline.Middle)
        font1 = QFont()
        font1.setWeight(QFont.Weight.Bold)
        font1.setItalic(True)
        font1.setPixelSize(round(size * 0.08))
        p.setFont(font1)
        p.setFillStyle(QColor(0xB0D040))
        p.fillText("HELLO", centerX, centerY - size * 0.18)

        # QCanvasPainter text
        font2 = QFont()
        font2.setWeight(QFont.Weight.Thin)
        font2.setPixelSize(round(size * 0.11))
        p.setFont(font2)
        p.fillText("Qt Canvas Painter", centerX, centerY - size * 0.08)

        # Paint heart
        pattern = QCanvasImagePattern(self.m_image, centerX, centerY, size * 0.08, size * 0.05)
        p.setFillStyle(pattern)
        p.setLineCap(QCanvasPainter.LineCap.Round)
        p.setStrokeStyle(QColor(0xB0D040))
        p.beginPath()
        p.moveTo(centerX, centerY + size * 0.3)
        p.bezierCurveTo(centerX - size * 0.25, centerY + size * 0.1,
                        centerX - size * 0.05, centerY + size * 0.05,
                        centerX, centerY + size * 0.15)
        p.bezierCurveTo(centerX + size * 0.05, centerY + size * 0.05,
                        centerX + size * 0.25, centerY + size * 0.1,
                        centerX, centerY + size * 0.3)
        p.stroke()
        p.fill()
