# Copyright (C) 2023 The Qt Company Ltd.
# Copyright (C) 2013 Riverbank Computing Limited.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import ctypes
from PySide6.QtCore import Signal, Slot, Qt, QSize, QPointF
from PySide6.QtGui import (QVector3D, QOpenGLFunctions,
                           QMatrix4x4, QOpenGLContext, QSurfaceFormat)
from PySide6.QtOpenGL import (QOpenGLVertexArrayObject, QOpenGLBuffer,
                              QOpenGLShaderProgram, QOpenGLShader)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL import GL

from shiboken6 import VoidPtr
from logo import Logo

FRAGMENT_SHADER_SOURCE_CORE = """#version 150
in highp vec3 vert;
in highp vec3 vertNormal;
out highp vec4 fragColor;
uniform highp vec3 lightPos;
void main() {
   highp vec3 L = normalize(lightPos - vert);
   highp float NL = max(dot(normalize(vertNormal), L), 0.0);
   highp vec3 color = vec3(0.39, 1.0, 0.0);
   highp vec3 col = clamp(color * 0.2 + color * 0.8 * NL, 0.0, 1.0);
   fragColor = vec4(col, 1.0);
}"""


FRAGMENT_SHADER_SOURCE = """varying highp vec3 vert;
varying highp vec3 vertNormal;
uniform highp vec3 lightPos;
void main() {
   highp vec3 L = normalize(lightPos - vert);
   highp float NL = max(dot(normalize(vertNormal), L), 0.0);
   highp vec3 color = vec3(0.39, 1.0, 0.0);
   highp vec3 col = clamp(color * 0.2 + color * 0.8 * NL, 0.0, 1.0);
   gl_FragColor = vec4(col, 1.0);
}"""


VERTEX_SHADER_SOURCE_CORE = """#version 150
in vec4 vertex;
in vec3 normal;
out vec3 vert;
out vec3 vertNormal;
uniform mat4 projMatrix;
uniform mat4 mvMatrix;
uniform mat3 normalMatrix;
void main() {
   vert = vertex.xyz;
   vertNormal = normalMatrix * normal;
   gl_Position = projMatrix * mvMatrix * vertex;
}"""


VERTEX_SHADER_SOURCE = """attribute vec4 vertex;
attribute vec3 normal;
varying vec3 vert;
varying vec3 vertNormal;
uniform mat4 projMatrix;
uniform mat4 mvMatrix;
uniform mat3 normalMatrix;
void main() {
   vert = vertex.xyz;
   vertNormal = normalMatrix * normal;
   gl_Position = projMatrix * mvMatrix * vertex;
}"""


class GLWidget(QOpenGLWidget, QOpenGLFunctions):
    x_rotation_changed = Signal(int)
    y_rotation_changed = Signal(int)
    z_rotation_changed = Signal(int)

    _transparent = False

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)

        self._core = QSurfaceFormat.defaultFormat().profile() == QSurfaceFormat.CoreProfile

        self._x_rot = 0
        self._y_rot = 0
        self._z_rot = 0
        self._last_pos = QPointF()
        self.logo = Logo()
        self.vao = QOpenGLVertexArrayObject()
        self._logo_vbo = QOpenGLBuffer()
        self.program = QOpenGLShaderProgram()
        self._proj_matrix_loc = 0
        self._mv_matrix_loc = 0
        self._normal_matrix_loc = 0
        self._light_pos_loc = 0
        self.proj = QMatrix4x4()
        self.camera = QMatrix4x4()
        self.world = QMatrix4x4()
        if self._transparent:
            fmt = self.format()
            fmt.setAlphaBufferSize(8)
            self.setFormat(fmt)

    @staticmethod
    def set_transparent(t):
        GLWidget._transparent = t

    @staticmethod
    def is_transparent():
        return GLWidget._transparent

    def x_rotation(self):
        return self._x_rot

    def y_rotation(self):
        return self._y_rot

    def z_rotation(self):
        return self._z_rot

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def normalize_angle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    @Slot(int)
    def set_xrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._x_rot:
            self._x_rot = angle
            self.x_rotation_changed.emit(angle)
            self.update()

    @Slot(int)
    def set_yrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._y_rot:
            self._y_rot = angle
            self.y_rotation_changed.emit(angle)
            self.update()

    @Slot(int)
    def set_zrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._z_rot:
            self._z_rot = angle
            self.z_rotation_changed.emit(angle)
            self.update()

    @Slot()
    def cleanup(self):
        if self.program:
            self.makeCurrent()
            self._logo_vbo.destroy()
            del self.program
            self.program = None
            self.doneCurrent()

    def initializeGL(self):
        self.initializeOpenGLFunctions()
        self.glClearColor(0, 0, 0, 0 if self._transparent else 1)

        self.program = QOpenGLShaderProgram()

        if self._core:
            self._vertex_shader = VERTEX_SHADER_SOURCE_CORE
            self._fragment_shader = FRAGMENT_SHADER_SOURCE_CORE
        else:
            self._vertex_shader = VERTEX_SHADER_SOURCE
            self._fragment_shader = FRAGMENT_SHADER_SOURCE

        self.program.addShaderFromSourceCode(QOpenGLShader.Vertex,
                                             self._vertex_shader)
        self.program.addShaderFromSourceCode(QOpenGLShader.Fragment,
                                             self._fragment_shader)
        self.program.bindAttributeLocation("vertex", 0)
        self.program.bindAttributeLocation("normal", 1)
        self.program.link()

        self.program.bind()
        self._proj_matrix_loc = self.program.uniformLocation("projMatrix")
        self._mv_matrix_loc = self.program.uniformLocation("mvMatrix")
        self._normal_matrix_loc = self.program.uniformLocation("normalMatrix")
        self._light_pos_loc = self.program.uniformLocation("lightPos")

        self.vao.create()
        with QOpenGLVertexArrayObject.Binder(self.vao):
            self._logo_vbo.create()
            self._logo_vbo.bind()
            float_size = ctypes.sizeof(ctypes.c_float)
            self._logo_vbo.allocate(self.logo.const_data(),
                                    self.logo.count() * float_size)

            self.setup_vertex_attribs()

            self.camera.setToIdentity()
            self.camera.translate(0, 0, -1)

            self.program.setUniformValue(self._light_pos_loc,
                                         QVector3D(0, 0, 70))
            self.program.release()

    def setup_vertex_attribs(self):
        self._logo_vbo.bind()
        f = QOpenGLContext.currentContext().functions()
        f.glEnableVertexAttribArray(0)
        f.glEnableVertexAttribArray(1)
        float_size = ctypes.sizeof(ctypes.c_float)

        null = VoidPtr(0)
        pointer = VoidPtr(3 * float_size)
        f.glVertexAttribPointer(0, 3, int(GL.GL_FLOAT), int(GL.GL_FALSE),
                                6 * float_size, null)
        f.glVertexAttribPointer(1, 3, int(GL.GL_FLOAT), int(GL.GL_FALSE),
                                6 * float_size, pointer)
        self._logo_vbo.release()

    def paintGL(self):
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.glEnable(GL.GL_DEPTH_TEST)
        self.glEnable(GL.GL_CULL_FACE)

        self.world.setToIdentity()
        self.world.rotate(180 - (self._x_rot / 16), 1, 0, 0)
        self.world.rotate(self._y_rot / 16, 0, 1, 0)
        self.world.rotate(self._z_rot / 16, 0, 0, 1)

        with QOpenGLVertexArrayObject.Binder(self.vao):
            self.program.bind()
            self.program.setUniformValue(self._proj_matrix_loc, self.proj)
            self.program.setUniformValue(self._mv_matrix_loc,
                                         self.camera * self.world)
            normal_matrix = self.world.normalMatrix()
            self.program.setUniformValue(self._normal_matrix_loc, normal_matrix)

            self.glDrawArrays(GL.GL_TRIANGLES, 0, self.logo.vertex_count())
            self.program.release()

    def resizeGL(self, width, height):
        self.proj.setToIdentity()
        self.proj.perspective(45, width / height, 0.01, 100)

    def hideEvent(self, event):
        self.cleanup()
        super().hideEvent(event)

    def mousePressEvent(self, event):
        self._last_pos = event.position()

    def mouseMoveEvent(self, event):
        pos = event.position()
        dx = pos.x() - self._last_pos.x()
        dy = pos.y() - self._last_pos.y()

        if event.buttons() & Qt.LeftButton:
            self.set_xrotation(self._x_rot + 8 * dy)
            self.set_yrotation(self._y_rot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.set_xrotation(self._x_rot + 8 * dy)
            self.set_zrotation(self._z_rot + 8 * dx)

        self._last_pos = pos
