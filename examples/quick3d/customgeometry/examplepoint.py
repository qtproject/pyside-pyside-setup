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
