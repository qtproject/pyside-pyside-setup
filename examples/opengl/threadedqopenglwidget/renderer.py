# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import ctypes
import math
import numpy

from OpenGL import GL

from PySide6.QtOpenGL import QOpenGLShader, QOpenGLShaderProgram, QOpenGLBuffer
from PySide6.QtGui import (QGuiApplication, QOpenGLFunctions, QVector3D,
                           QMatrix4x4)
from PySide6.QtCore import (QElapsedTimer, QObject, QMetaObject, QMutex,
                            QMutexLocker, QThread, QWaitCondition, Signal, Slot)

# Some OpenGL implementations have serious issues with compiling and linking
# shaders on multiple threads concurrently. Avoid self.
init_mutex = QMutex()


VERTEX_SHADER = """attribute highp vec4 vertex;
attribute mediump vec3 normal;
uniform mediump mat4 matrix;
varying mediump vec4 color;
void main(void)
{
    vec3 toLight = normalize(vec3(0.0, 0.3, 1.0));
    float angle = max(dot(normal, toLight), 0.0);
    vec3 col = vec3(0.40, 1.0, 0.0);
    color = vec4(col * 0.2 + col * 0.8 * angle, 1.0);
    color = clamp(color, 0.0, 1.0);
    gl_Position = matrix * vertex;
}
"""


FRAGMENT_SHADER = """varying mediump vec4 color;
void main(void)
{
    gl_FragColor = color;
}
"""


class Renderer(QObject, QOpenGLFunctions):

    context_wanted = Signal()

    def __init__(self, widget):
        QObject.__init__(self)
        QOpenGLFunctions.__init__(self)
        self._glwidget = widget
        self._inited = False
        self._fAngle = 0
        self._fScale = 1

        self._vertices = []
        self._normals = []
        self._program = QOpenGLShaderProgram()
        self._vbo = QOpenGLBuffer()
        self._vertex_attr = 0
        self._normal_attr = 0
        self._matrix_uniform = 0
        self._renderMutex = QMutex()
        self._elapsed = QElapsedTimer()
        self._grabMutex = QMutex()
        self._grab_condition = QWaitCondition()
        self._exiting = False

    def lock_renderer(self):
        self._renderMutex.lock()

    def unlock_renderer(self):
        self._renderMutex.unlock()

    def grab_mutex(self):
        return self._grabMutex

    def grab_condition(self):
        return self._grab_condition

    def prepare_exit(self):
        self._exiting = True
        self._grab_condition.wakeAll()

    def paint_Qt_logo(self):
        self._vbo.bind()
        self._program.setAttributeBuffer(self._vertex_attr, GL.GL_FLOAT, 0, 3)
        size = len(self._vertices) * 3 * ctypes.sizeof(ctypes.c_float)
        self._program.setAttributeBuffer(self._normal_attr, GL.GL_FLOAT, size, 3)
        self._vbo.release()

        self._program.enableAttributeArray(self._vertex_attr)
        self._program.enableAttributeArray(self._normal_attr)

        self.glDrawArrays(GL.GL_TRIANGLES, 0, len(self._vertices))

        self._program.disableAttributeArray(self._normal_attr)
        self._program.disableAttributeArray(self._vertex_attr)

    @Slot()
    def render(self):
        global init_mutex

        if self._exiting:
            return

        ctx = self._glwidget.context()
        if not ctx:  # QOpenGLWidget not yet initialized
            return

        # Grab the context.
        self._grabMutex.lock()
        self.context_wanted.emit()
        self._grab_condition.wait(self._grabMutex)

        with QMutexLocker(self._renderMutex):
            self._grabMutex.unlock()

            if self._exiting:
                return

            assert(ctx.thread() == QThread.currentThread())

            # Make the context (and an offscreen surface) current for self thread.
            # The QOpenGLWidget's fbo is bound in the context.
            self._glwidget.makeCurrent()

            if not self._inited:
                self._inited = True
                self.initializeOpenGLFunctions()
                with QMutexLocker(init_mutex):
                    self._init_gl()
                self._elapsed.start()

            self._render_next()

            # Make no context current on self thread and move the
            # QOpenGLWidget'scontext back to the gui thread.
            self._glwidget.doneCurrent()
            ctx.moveToThread(QGuiApplication.instance().thread())

            # Schedule composition. Note that self will use QueuedConnection,
            # meaning that update() will be invoked on the gui thread.
            QMetaObject.invokeMethod(self._glwidget, "update")

    def _init_gl(self):
        vshader = QOpenGLShader(QOpenGLShader.Vertex, self)
        vshader.compileSourceCode(VERTEX_SHADER)

        fshader = QOpenGLShader(QOpenGLShader.Fragment, self)
        fshader.compileSourceCode(FRAGMENT_SHADER)

        self._program.addShader(vshader)
        self._program.addShader(fshader)
        self._program.link()

        self._vertex_attr = self._program.attributeLocation("vertex")
        self._normal_attr = self._program.attributeLocation("normal")
        self._matrix_uniform = self._program.uniformLocation("matrix")

        self._fAngle = 0
        self._fScale = 1
        self.create_geometry()

        self._vbo.create()
        self._vbo.bind()

        data_count = len(self._vertices) * 2 * 3
        data = numpy.empty(data_count, dtype=ctypes.c_float)
        i = 0
        for v in self._vertices:
            data[i] = v.x()
            i += 1
            data[i] = v.y()
            i += 1
            data[i] = v.z()
            i += 1
        for n in self._normals:
            data[i] = n.x()
            i += 1
            data[i] = n.y()
            i += 1
            data[i] = n.z()
            i += 1

        vertices_size = data_count * ctypes.sizeof(ctypes.c_float)
        self._vbo.allocate(data.tobytes(), vertices_size)

    def _render_next(self):
        self.glClearColor(0.1, 0.2, 0.2, 1.0)
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.glFrontFace(GL.GL_CW)
        self.glCullFace(GL.GL_FRONT)
        self.glEnable(GL.GL_CULL_FACE)
        self.glEnable(GL.GL_DEPTH_TEST)

        modelview = QMatrix4x4()
        modelview.rotate(self._fAngle, 0.0, 1.0, 0.0)
        modelview.rotate(self._fAngle, 1.0, 0.0, 0.0)
        modelview.rotate(self._fAngle, 0.0, 0.0, 1.0)
        modelview.scale(self._fScale)
        modelview.translate(0.0, -0.2, 0.0)

        self._program.bind()
        self._program.setUniformValue(self._matrix_uniform, modelview)
        self.paint_Qt_logo()
        self._program.release()

        self.glDisable(GL.GL_DEPTH_TEST)
        self.glDisable(GL.GL_CULL_FACE)

        self._fAngle += 1.0

    def create_geometry(self):
        self._vertices = []
        self._normals = []

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        NUM_SECTORS = 100
        SECTOR_ANGLE = 2 * math.pi / NUM_SECTORS

        for i in range(NUM_SECTORS):
            angle = i * SECTOR_ANGLE
            sin_angle = math.sin(angle)
            cos_angle = math.cos(angle)
            x5 = 0.30 * sin_angle
            y5 = 0.30 * cos_angle
            x6 = 0.20 * sin_angle
            y6 = 0.20 * cos_angle

            angle += SECTOR_ANGLE
            sin_angle = math.sin(angle)
            cos_angle = math.cos(angle)
            x7 = 0.20 * sin_angle
            y7 = 0.20 * cos_angle
            x8 = 0.30 * sin_angle
            y8 = 0.30 * cos_angle

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        for i in range(len(self._vertices)):
            self._vertices[i] *= 2.0

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):

        self._vertices.append(QVector3D(x1, y1, -0.05))
        self._vertices.append(QVector3D(x2, y2, -0.05))
        self._vertices.append(QVector3D(x4, y4, -0.05))

        self._vertices.append(QVector3D(x3, y3, -0.05))
        self._vertices.append(QVector3D(x4, y4, -0.05))
        self._vertices.append(QVector3D(x2, y2, -0.05))

        n = QVector3D.normal(QVector3D(x2 - x1, y2 - y1, 0.0),
                             QVector3D(x4 - x1, y4 - y1, 0.0))

        self._normals.append(n)
        self._normals.append(n)
        self._normals.append(n)

        self._normals.append(n)
        self._normals.append(n)
        self._normals.append(n)

        self._vertices.append(QVector3D(x4, y4, 0.05))
        self._vertices.append(QVector3D(x2, y2, 0.05))
        self._vertices.append(QVector3D(x1, y1, 0.05))

        self._vertices.append(QVector3D(x2, y2, 0.05))
        self._vertices.append(QVector3D(x4, y4, 0.05))
        self._vertices.append(QVector3D(x3, y3, 0.05))

        n = QVector3D.normal(QVector3D(x2 - x4, y2 - y4, 0.0),
                             QVector3D(x1 - x4, y1 - y4, 0.0))

        self._normals.append(n)
        self._normals.append(n)
        self._normals.append(n)

        self._normals.append(n)
        self._normals.append(n)
        self._normals.append(n)

    def extrude(self, x1, y1, x2, y2):
        self._vertices.append(QVector3D(x1, y1, +0.05))
        self._vertices.append(QVector3D(x2, y2, +0.05))
        self._vertices.append(QVector3D(x1, y1, -0.05))

        self._vertices.append(QVector3D(x2, y2, -0.05))
        self._vertices.append(QVector3D(x1, y1, -0.05))
        self._vertices.append(QVector3D(x2, y2, +0.05))

        n = QVector3D.normal(QVector3D(x2 - x1, y2 - y1, 0.0),
                             QVector3D(0.0, 0.0, -0.1))

        self._normals.append(n)
        self._normals.append(n)
        self._normals.append(n)

        self._normals.append(n)
        self._normals.append(n)
        self._normals.append(n)
