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
from PySide6.QtCore import QPointF, QUrl
from PySide6.QtQmlFeatures import auto_properties, effect

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "CustomGeometry"
QML_IMPORT_MAJOR_VERSION = 1


# @auto_properties turns the plain self.p1/p2/p3/p4/segmentCount assignments
# in __init__ into Q_PROPERTYs with change-notification signals, so QML can
# bind to them. The @effect method centralises the self.update() call that
# triggers a repaint whenever any control-point or segment-count changes.
@QmlElement
@auto_properties
class BezierCurve(QQuickItem):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.p1 = QPointF(0, 0)
        self.p2 = QPointF(1, 0)
        self.p3 = QPointF(0, 1)
        self.p4 = QPointF(1, 1)
        self.segmentCount = 32

        self._node = None
        self._geometry = None
        self.setFlag(QQuickItem.Flag.ItemHasContents, True)

    @effect("p1", "p2", "p3", "p4", "segmentCount")
    def _on_geometry_changed(self):
        self.update()

    def updatePaintNode(self, oldNode, updatePaintNodeData):
        self._node = oldNode
        if not self._node:
            self._default_attributes = QSGGeometry.defaultAttributes_Point2D()
            self._geometry = QSGGeometry(self._default_attributes, self.segmentCount)
            self._geometry.setLineWidth(2)
            self._geometry.setDrawingMode(QSGGeometry.DrawingMode.DrawLineStrip)

            self._node = QSGGeometryNode()
            self._node.setGeometry(self._geometry)
            self._node.setFlag(QSGNode.Flag.OwnsGeometry)
            self._material = QSGFlatColorMaterial()
            self._material.setColor(QColor(255, 0, 0))
            self._node.setMaterial(self._material)
            self._node.setFlag(QSGNode.Flag.OwnsMaterial)
        else:
            self._geometry = self._node.geometry()
            self._geometry.allocate(self.segmentCount)

        item_size = self.size()
        item_width = float(item_size.width())
        item_height = float(item_size.height())
        vertices = self._geometry.vertexDataAsPoint2D()
        for i in range(self.segmentCount):
            t = float(i) / float(self.segmentCount - 1)
            inv_t = 1 - t
            pos = ((inv_t * inv_t * inv_t * self.p1)
                   + (3 * inv_t * inv_t * t * self.p2)
                   + (3 * inv_t * t * t * self.p3)
                   + (t * t * t * self.p4))
            vertices[i].set(pos.x() * item_width, pos.y() * item_height)

        self._geometry.setVertexDataAsPoint2D(vertices)

        self._node.markDirty(QSGNode.DirtyStateBit.DirtyGeometry)
        return self._node


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
