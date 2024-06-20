# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Property, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtQml import QmlElement

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Charts"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PieSlice(QQuickPaintedItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._color = QColor()
        self._from_angle = 0
        self._angle_span = 0

    @Property(QColor, final=True)
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = QColor(color)

    @Property(int, final=True)
    def fromAngle(self):
        return self._from_angle

    @fromAngle.setter
    def fromAngle(self, fromAngle):
        self._from_angle = fromAngle

    @Property(int, final=True)
    def angleSpan(self):
        return self._angle_span

    @angleSpan.setter
    def angleSpan(self, angleSpan):
        self._angle_span = angleSpan

    def paint(self, painter):
        painter.setPen(QPen(self._color, 2))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(0, 0, self.width(), self.height()).adjusted(1, 1, -1, -1)
        painter.drawPie(rect, self._from_angle * 16, self._angle_span * 16)
