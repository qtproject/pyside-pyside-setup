# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtQml import QmlElement
from PySide6.QtCore import QPointF, Qt, Property, Signal
from PySide6.QtQuick import QQuickPaintedItem

QML_IMPORT_NAME = "TextBalloon"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional


@QmlElement
class TextBalloon(QQuickPaintedItem):

    rightAlignedChanged = Signal()

    def __init__(self, parent=None):
        self._rightAligned = False
        super().__init__(parent)

    @Property(bool, notify=rightAlignedChanged)
    def rightAligned(self):
        return self._rightAligned

    @rightAligned.setter
    def rightAligned(self, value):
        self._rightAligned = value
        self.rightAlignedChanged.emit()

    def paint(self, painter: QPainter):

        brush = QBrush(QColor("#007430"))

        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        itemSize = self.size()

        painter.drawRoundedRect(0, 0, itemSize.width(), itemSize.height() - 10, 10, 10)

        if self.rightAligned:
            points = [
                QPointF(itemSize.width() - 10.0, itemSize.height() - 10.0),
                QPointF(itemSize.width() - 20.0, itemSize.height()),
                QPointF(itemSize.width() - 30.0, itemSize.height() - 10.0),
            ]
        else:
            points = [
                QPointF(10.0, itemSize.height() - 10.0),
                QPointF(20.0, itemSize.height()),
                QPointF(30.0, itemSize.height() - 10.0),
            ]
        painter.drawConvexPolygon(points)
