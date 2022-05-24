# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import random

import numpy as np
from PySide6.QtGui import QVector3D
from PySide6.QtQml import QmlElement
from PySide6.QtQuick3D import QQuick3DGeometry

QML_IMPORT_NAME = "ExamplePointGeometry"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class ExamplePointGeometry(QQuick3DGeometry):
    def __init__(self, parent=None):
        QQuick3DGeometry.__init__(self, parent)
        self.updateData()

    def updateData(self):
        self.clear()

        # We use numpy arrays to handle the vertex data,
        # but still we need to consider the 'sizeof(float)'
        # from C to set the Stride, and Attributes for the
        # underlying Qt methods
        FLOAT_SIZE = 4
        NUM_POINTS = 2000
        stride = 3

        vertexData = np.zeros(NUM_POINTS * stride, dtype=np.float32)

        p = 0
        for i in range(NUM_POINTS):
            vertexData[p] = random.uniform(-5.0, +5.0)
            p += 1
            vertexData[p] = random.uniform(-5.0, +5.0)
            p += 1
            vertexData[p] = 0.0
            p += 1

        self.setVertexData(vertexData.tobytes())
        self.setStride(stride * FLOAT_SIZE)
        self.setBounds(QVector3D(-5.0, -5.0, 0.0), QVector3D(+5.0, +5.0, 0.0))

        self.setPrimitiveType(QQuick3DGeometry.PrimitiveType.Points)

        self.addAttribute(
            QQuick3DGeometry.Attribute.PositionSemantic, 0, QQuick3DGeometry.Attribute.F32Type
        )
