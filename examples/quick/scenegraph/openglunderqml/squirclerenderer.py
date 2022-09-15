# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from textwrap import dedent

import numpy as np
from OpenGL.GL import (GL_ARRAY_BUFFER, GL_BLEND, GL_DEPTH_TEST, GL_FLOAT,
                       GL_ONE, GL_SRC_ALPHA, GL_TRIANGLE_STRIP)
from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QOpenGLFunctions
from PySide6.QtOpenGL import (QOpenGLShader, QOpenGLShaderProgram,
                              QOpenGLVersionProfile)
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface

VERTEX_SHADER = dedent(
    """\
    attribute highp vec4 vertices;
    varying highp vec2 coords;
    void main() {
        gl_Position = vertices;
        coords = vertices.xy;
    }
    """
)
FRAGMENT_SHADER = dedent(
    """\
    uniform lowp float t;
    varying highp vec2 coords;
    void main() {
        lowp float i = 1. - (pow(abs(coords.x), 4.) + pow(abs(coords.y), 4.));
        i = smoothstep(t - 0.8, t + 0.8, i);
        i = floor(i * 20.) / 20.;
        gl_FragColor = vec4(coords * .5 + .5, i, i);
    }
    """
)


class SquircleRenderer(QOpenGLFunctions):
    def __init__(self):
        QOpenGLFunctions.__init__(self)
        self._viewport_size = QSize()
        self._t = 0.0
        self._program = None
        self._window = QQuickWindow()

    def setT(self, t):
        self._t = t

    def setViewportSize(self, size):
        self._viewport_size = size

    def setWindow(self, window):
        self._window = window

    @Slot()
    def init(self):
        if not self._program:
            rif = self._window.rendererInterface()
            assert (rif.graphicsApi() == QSGRendererInterface.OpenGL)
            self.initializeOpenGLFunctions()
            self._program = QOpenGLShaderProgram()
            self._program.addCacheableShaderFromSourceCode(QOpenGLShader.Vertex, VERTEX_SHADER)
            self._program.addCacheableShaderFromSourceCode(QOpenGLShader.Fragment, FRAGMENT_SHADER)
            self._program.bindAttributeLocation("vertices", 0)
            self._program.link()

    @Slot()
    def paint(self):
        # Play nice with the RHI. Not strictly needed when the scenegraph uses
        # OpenGL directly.
        self._window.beginExternalCommands()

        self._program.bind()

        self._program.enableAttributeArray(0)

        values = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="single")

        # This example relies on (deprecated) client-side pointers for the vertex
        # input. Therefore, we have to make sure no vertex buffer is bound.
        self.glBindBuffer(GL_ARRAY_BUFFER, 0)

        self._program.setAttributeArray(0, GL_FLOAT, values, 2)
        self._program.setUniformValue1f("t", self._t)

        self.glViewport(0, 0, self._viewport_size.width(), self._viewport_size.height())

        self.glDisable(GL_DEPTH_TEST)

        self.glEnable(GL_BLEND)
        self.glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        self.glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        self._program.disableAttributeArray(0)
        self._program.release()

        self._window.endExternalCommands()
