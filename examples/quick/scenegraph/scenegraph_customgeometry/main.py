# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt Quick customgeometry example from Qt v6.x"""

import sys
from pathlib import Path

from PySide6.QtQuick import (QQuickView, QQuickItem, QSGNode, QSGGeometryNode,
                             QSGGeometry, QSGFlatColorMaterial)
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QGuiApplication, QColor
from PySide6.QtCore import (QPointF, QUrl, Property, Signal, Slot)

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "CustomGeometry"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class BezierCurve(QQuickItem):
    p1Changed = Signal()
    p2Changed = Signal()
    p3Changed = Signal()
    p4Changed = Signal()
    segmentCountChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._p1 = QPointF(0, 0)
        self._p2 = QPointF(1, 0)
        self._p3 = QPointF(0, 1)
        self._p4 = QPointF(1, 1)
        self._segmentCount = 32

        self._node = None
        self._geometry = None
        self.setFlag(QQuickItem.Flags.ItemHasContents, True)

    def p1(self):
        return self._p1

    def p2(self):
        return self._p2

    def p3(self):
        return self._p3

    def p4(self):
        return self._p4

    def segmentCount(self):
        return self._segmentCount

    @Slot(QPointF)
    def setP1(self, p):
        if p != self._p1:
            self._p1 = p
            self.p1Changed.emit()
            self.update()

    @Slot(QPointF)
    def setP2(self, p):
        if p != self._p2:
            self._p2 = p
            self.p2Changed.emit()
            self.update()

    @Slot(QPointF)
    def setP3(self, p):
        if p != self._p3:
            self._p3 = p
            self.p3Changed.emit()
            self.update()

    @Slot(QPointF)
    def setP4(self, p):
        if p != self._p4:
            self._p4 = p
            self.p4Changed.emit()
            self.update()

    @Slot(int)
    def setSegmentCount(self, p):
        if p != self._segmentCount:
            self._segmentCount = p
            self.segmentCountChanged.emit()
            self.update()

    def updatePaintNode(self, oldNode, updatePaintNodeData):
        self._node = oldNode
        if not self._node:
            self._default_attributes = QSGGeometry.defaultAttributes_Point2D()
            self._geometry = QSGGeometry(self._default_attributes, self._segmentCount)
            self._geometry.setLineWidth(2)
            self._geometry.setDrawingMode(QSGGeometry.DrawingMode.DrawLineStrip)

            self._node = QSGGeometryNode()
            self._node.setGeometry(self._geometry)
            self._node.setFlag(QSGNode.Flags.OwnsGeometry)
            self._material = QSGFlatColorMaterial()
            self._material.setColor(QColor(255, 0, 0))
            self._node.setMaterial(self._material)
            self._node.setFlag(QSGNode.Flags.OwnsMaterial)
        else:
            self._geometry = self._node.geometry()
            self._geometry.allocate(self._segmentCount)

        item_size = self.size()
        item_width = float(item_size.width())
        item_height = float(item_size.height())
        vertices = self._geometry.vertexDataAsPoint2D()
        for i in range(self._segmentCount):
            t = float(i) / float(self._segmentCount - 1)
            inv_t = 1 - t
            pos = ((inv_t * inv_t * inv_t * self._p1)
                   + (3 * inv_t * inv_t * t * self._p2)
                   + (3 * inv_t * t * t * self._p3)
                   + (t * t * t * self._p4))
            vertices[i].set(pos.x() * item_width, pos.y() * item_height)

        self._geometry.setVertexDataAsPoint2D(vertices)

        self._node.markDirty(QSGNode.DirtyGeometry)
        return self._node

    p1 = Property(QPointF, p1, setP1, notify=p1Changed)
    p2 = Property(QPointF, p2, setP2, notify=p2Changed)
    p3 = Property(QPointF, p3, setP3, notify=p3Changed)
    p4 = Property(QPointF, p4, setP4, notify=p4Changed)

    segmentCount = Property(int, segmentCount, setSegmentCount,
                            notify=segmentCountChanged)


if __name__ == "__main__":
    app = QGuiApplication([])
    view = QQuickView()
    format = view.format()
    format.setSamples(16)
    view.setFormat(format)

    qml_file = Path(__file__).parent / "main.qml"
    view.setSource(QUrl.fromLocalFile(qml_file))
    if not view.rootObject():
        sys.exit(-1)
    view.show()
    ex = app.exec()
    del view
    sys.exit(ex)
