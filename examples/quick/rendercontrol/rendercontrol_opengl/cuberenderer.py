# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import ctypes
import numpy
from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_CULL_FACE, GL_CW,
                       GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FALSE, GL_FLOAT,
                       GL_TEXTURE_2D, GL_TRIANGLES)

from PySide6.QtGui import (QMatrix4x4, QOffscreenSurface, QOpenGLContext,
                           QOpenGLFunctions, QWindow)
from PySide6.QtOpenGL import (QOpenGLBuffer, QOpenGLShader,
                              QOpenGLShaderProgram, QOpenGLVertexArrayObject)
from shiboken6 import VoidPtr


VERTEXSHADER_SOURCE = """attribute highp vec4 vertex;
attribute lowp vec2 coord;
varying lowp vec2 v_coord;
uniform highp mat4 matrix;
void main() {
   v_coord = coord;
   gl_Position = matrix * vertex;
}
"""


FRAGMENTSHADER_SOURCE = """varying lowp vec2 v_coord;
uniform sampler2D sampler;
void main() {
   gl_FragColor = vec4(texture2D(sampler, v_coord).rgb, 1.0);
}
"""


FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)


VERTEXES = numpy.array([-0.5, 0.5, 0.5, 0.5, -0.5, 0.5, -0.5, -0.5, 0.5,
                        0.5, -0.5, 0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
                        -0.5, -0.5, -0.5, 0.5, -0.5, -0.5, -0.5, 0.5, -0.5,
                        0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5, -0.5, -0.5,

                        0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, 0.5, -0.5,
                        0.5, 0.5, 0.5, 0.5, 0.5, -0.5, 0.5, -0.5, 0.5,
                        -0.5, 0.5, -0.5, -0.5, -0.5, 0.5, -0.5, -0.5, -0.5,
                        -0.5, -0.5, 0.5, -0.5, 0.5, -0.5, -0.5, 0.5, 0.5,

                        0.5, 0.5,  -0.5, -0.5, 0.5,  0.5,  -0.5,  0.5,  -0.5,
                        -0.5,  0.5,  0.5,  0.5,  0.5,  -0.5, 0.5, 0.5,  0.5,
                        -0.5,  -0.5, -0.5, -0.5, -0.5, 0.5,  0.5, -0.5, -0.5,
                        0.5, -0.5, 0.5,  0.5,  -0.5, -0.5, -0.5,  -0.5, 0.5],
                       dtype=numpy.float32)


TEX_COORDS = numpy.array([0.0, 0.0,  1.0, 1.0,  1.0, 0.0,
                          1.0, 1.0,  0.0, 0.0,  0.0, 1.0,
                          1.0, 1.0,  1.0, 0.0,  0.0, 1.0,
                          0.0, 0.0,  0.0, 1.0,  1.0, 0.0,

                          1.0, 1.0,  1.0, 0.0,  0.0, 1.0,
                          0.0, 0.0,  0.0, 1.0,  1.0, 0.0,
                          0.0, 0.0,  1.0, 1.0,  1.0, 0.0,
                          1.0, 1.0,  0.0, 0.0,  0.0, 1.0,

                          0.0, 1.0,  1.0, 0.0,  1.0, 1.0,
                          1.0, 0.0,  0.0, 1.0,  0.0, 0.0,
                          1.0, 0.0,  1.0, 1.0,  0.0, 0.0,
                          0.0, 1.0,  0.0, 0.0,  1.0, 1.0], dtype=numpy.float32)


class CubeRenderer():
    def __init__(self, offscreenSurface):
        self.m_angle = 0
        self.m_offscreenSurface = offscreenSurface
        self.m_context = None
        self.m_program = None
        self.m_vbo = None
        self.m_vao = None
        self.m_matrixLoc = 0
        self.m_proj = QMatrix4x4()

    def __del__(self):
        # Use a temporary offscreen surface to do the cleanup. There may not
        # be a native window surface available anymore at self stage.
        self.m_context.makeCurrent(self.m_offscreenSurface)
        del self.m_program
        del self.m_vbo
        del self.m_vao
        self.m_context.doneCurrent()

    def init(self, w, share):
        self.m_context = QOpenGLContext()
        self.m_context.setShareContext(share)
        self.m_context.setFormat(w.requestedFormat())
        self.m_context.create()
        if not self.m_context.makeCurrent(w):
            return

        f = self.m_context.functions()
        f.glClearColor(0.0, 0.1, 0.25, 1.0)
        f.glViewport(0, 0, w.width() * w.devicePixelRatio(),
                     w.height() * w.devicePixelRatio())

        self.m_program = QOpenGLShaderProgram()
        self.m_program.addCacheableShaderFromSourceCode(QOpenGLShader.Vertex,
                                                        VERTEXSHADER_SOURCE)
        self.m_program.addCacheableShaderFromSourceCode(QOpenGLShader.Fragment,
                                                        FRAGMENTSHADER_SOURCE)
        self.m_program.bindAttributeLocation("vertex", 0)
        self.m_program.bindAttributeLocation("coord", 1)
        self.m_program.link()
        self.m_matrixLoc = self.m_program.uniformLocation("matrix")

        self.m_vao = QOpenGLVertexArrayObject()
        self.m_vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.m_vao)

        self.m_vbo = QOpenGLBuffer()
        self.m_vbo.create()
        self.m_vbo.bind()

        vertexCount = 36
        self.m_vbo.allocate(FLOAT_SIZE * vertexCount * 5)
        vertex_data = VERTEXES.tobytes()
        tex_coord_data = TEX_COORDS.tobytes()
        self.m_vbo.write(0, VoidPtr(vertex_data),
                         FLOAT_SIZE * vertexCount * 3)
        self.m_vbo.write(FLOAT_SIZE * vertexCount * 3,
                         VoidPtr(tex_coord_data),
                         FLOAT_SIZE * vertexCount * 2)
        self.m_vbo.release()

        if self.m_vao.isCreated():
            self.setupVertexAttribs()

    def resize(self, w, h):
        self.m_proj.setToIdentity()
        self.m_proj.perspective(45, w / float(h), 0.01, 100.0)

    def setupVertexAttribs(self):
        self.m_vbo.bind()
        self.m_program.enableAttributeArray(0)
        self.m_program.enableAttributeArray(1)
        f = self.m_context.functions()

        null = VoidPtr(0)
        pointer = VoidPtr(36 * 3 * FLOAT_SIZE)
        f.glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, null)
        f.glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, pointer)
        self.m_vbo.release()

    def render(self, w, share, texture):
        if not self.m_context:
            self.init(w, share)

        if not self.m_context.makeCurrent(w):
            return

        f = self.m_context.functions()
        f.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if texture:
            f.glBindTexture(GL_TEXTURE_2D, texture)
            f.glFrontFace(GL_CW)  # because our cube's vertex data is such
            f.glEnable(GL_CULL_FACE)
            f.glEnable(GL_DEPTH_TEST)

            self.m_program.bind()
            vaoBinder = QOpenGLVertexArrayObject.Binder(self.m_vao)
            # If VAOs are not supported, set the vertex attributes every time.
            if not self.m_vao.isCreated():
                self.setupVertexAttribs()

            m = QMatrix4x4()
            m.translate(0, 0, -2)
            m.rotate(90, 0, 0, 1)
            m.rotate(self.m_angle, 0.5, 1, 0)
            self.m_angle += 0.5

            self.m_program.setUniformValue(self.m_matrixLoc, self.m_proj * m)

            # Draw the cube.
            f.glDrawArrays(GL_TRIANGLES, 0, 36)

        self.m_context.swapBuffers(w)
