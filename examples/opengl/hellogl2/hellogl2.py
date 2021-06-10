
############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
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
############################################################################

"""PySide6 port of the opengl/hellogl2 example from Qt v5.x"""

from argparse import ArgumentParser, RawTextHelpFormatter
import ctypes
import math
import numpy
import sys
from PySide6.QtCore import QCoreApplication, Signal, SIGNAL, SLOT, Qt, QSize, QPointF
from PySide6.QtGui import (QVector3D, QOpenGLFunctions,
    QMatrix4x4, QOpenGLContext, QSurfaceFormat)
from PySide6.QtOpenGL import (QOpenGLVertexArrayObject, QOpenGLBuffer,
    QOpenGLShaderProgram, QOpenGLShader)
from PySide6.QtWidgets import (QApplication, QWidget, QMessageBox, QHBoxLayout,
    QSlider)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from shiboken6 import VoidPtr

try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    message_box = QMessageBox(QMessageBox.Critical, "OpenGL hellogl",
                                         "PyOpenGL must be installed to run this example.",
                                         QMessageBox.Close)
    message_box.setDetailedText("Run:\npip install PyOpenGL PyOpenGL_accelerate")
    message_box.exec()
    sys.exit(1)


class Window(QWidget):
    def __init__(self, transparent, parent=None):
        QWidget.__init__(self, parent)

        if transparent:
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_NoSystemBackground, False)

        self._gl_widget = GLWidget(transparent)

        self._x_slider = self.create_slider()
        self._x_slider.valueChanged.connect(self._gl_widget.set_xrotation)
        self._gl_widget.x_rotation_changed.connect(self._x_slider.setValue)

        self._y_slider = self.create_slider()
        self._y_slider.valueChanged.connect(self._gl_widget.set_yrotation)
        self._gl_widget.y_rotation_changed.connect(self._y_slider.setValue)

        self._z_slider = self.create_slider()
        self._z_slider.valueChanged.connect(self._gl_widget.set_zrotation)
        self._gl_widget.z_rotation_changed.connect(self._z_slider.setValue)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self._gl_widget)
        main_layout.addWidget(self._x_slider)
        main_layout.addWidget(self._y_slider)
        main_layout.addWidget(self._z_slider)
        self.setLayout(main_layout)

        self._x_slider.setValue(15 * 16)
        self._y_slider.setValue(345 * 16)
        self._z_slider.setValue(0 * 16)

        self.setWindowTitle(self.tr("Hello GL"))

    def create_slider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)
        return slider

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(Window, self).keyPressEvent(event)


class Logo():
    def __init__(self):
        self.m_count = 0
        self.i = 0
        self.m_data = numpy.empty(2500 * 6, dtype=ctypes.c_float)

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

        for i in range(NUM_SECTORS):
            angle = (i * 2 * math.pi) / NUM_SECTORS
            x5 = 0.30 * math.sin(angle)
            y5 = 0.30 * math.cos(angle)
            x6 = 0.20 * math.sin(angle)
            y6 = 0.20 * math.cos(angle)

            angle = ((i + 1) * 2 * math.pi) / NUM_SECTORS
            x7 = 0.20 * math.sin(angle)
            y7 = 0.20 * math.cos(angle)
            x8 = 0.30 * math.sin(angle)
            y8 = 0.30 * math.cos(angle)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

    def const_data(self):
        return self.m_data.tobytes()

    def count(self):
        return self.m_count

    def vertex_count(self):
        return self.m_count / 6

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        n = QVector3D.normal(QVector3D(x4 - x1, y4 - y1, 0), QVector3D(x2 - x1, y2 - y1, 0))

        self.add(QVector3D(x1, y1, -0.05), n)
        self.add(QVector3D(x4, y4, -0.05), n)
        self.add(QVector3D(x2, y2, -0.05), n)

        self.add(QVector3D(x3, y3, -0.05), n)
        self.add(QVector3D(x2, y2, -0.05), n)
        self.add(QVector3D(x4, y4, -0.05), n)

        n = QVector3D.normal(QVector3D(x1 - x4, y1 - y4, 0), QVector3D(x2 - x4, y2 - y4, 0))

        self.add(QVector3D(x4, y4, 0.05), n)
        self.add(QVector3D(x1, y1, 0.05), n)
        self.add(QVector3D(x2, y2, 0.05), n)

        self.add(QVector3D(x2, y2, 0.05), n)
        self.add(QVector3D(x3, y3, 0.05), n)
        self.add(QVector3D(x4, y4, 0.05), n)

    def extrude(self, x1, y1, x2, y2):
        n = QVector3D.normal(QVector3D(0, 0, -0.1), QVector3D(x2 - x1, y2 - y1, 0))

        self.add(QVector3D(x1, y1, 0.05), n)
        self.add(QVector3D(x1, y1, -0.05), n)
        self.add(QVector3D(x2, y2, 0.05), n)

        self.add(QVector3D(x2, y2, -0.05), n)
        self.add(QVector3D(x2, y2, 0.05), n)
        self.add(QVector3D(x1, y1, -0.05), n)

    def add(self, v, n):
        self.m_data[self.i] = v.x()
        self.i += 1
        self.m_data[self.i] = v.y()
        self.i += 1
        self.m_data[self.i] = v.z()
        self.i += 1
        self.m_data[self.i] = n.x()
        self.i += 1
        self.m_data[self.i] = n.y()
        self.i += 1
        self.m_data[self.i] = n.z()
        self.i += 1
        self.m_count += 6


class GLWidget(QOpenGLWidget, QOpenGLFunctions):
    x_rotation_changed = Signal(int)
    y_rotation_changed = Signal(int)
    z_rotation_changed = Signal(int)

    def __init__(self, transparent, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)

        self._transparent = transparent
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
        if transparent:
            fmt = self.format()
            fmt.setAlphaBufferSize(8)
            self.setFormat(fmt)

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

    def set_xrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._x_rot:
            self._x_rot = angle
            self.x_rotation_changed.emit(angle)
            self.update()

    def set_yrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._y_rot:
            self._y_rot = angle
            self.y_rotation_changed.emit(angle)
            self.update()

    def set_zrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._z_rot:
            self._z_rot = angle
            self.z_rotation_changed.emit(angle)
            self.update()

    def cleanup(self):
        self.makeCurrent()
        self._logo_vbo.destroy()
        del self.program
        self.program = None
        self.doneCurrent()

    def vertex_shader_source_core(self):
        return """#version 150
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

    def fragment_shader_source_core(self):
        return """#version 150
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

    def vertex_shader_source(self):
        return """attribute vec4 vertex;
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

    def fragment_shader_source(self):
        return """varying highp vec3 vert;
                varying highp vec3 vertNormal;
                uniform highp vec3 lightPos;
                void main() {
                   highp vec3 L = normalize(lightPos - vert);
                   highp float NL = max(dot(normalize(vertNormal), L), 0.0);
                   highp vec3 color = vec3(0.39, 1.0, 0.0);
                   highp vec3 col = clamp(color * 0.2 + color * 0.8 * NL, 0.0, 1.0);
                   gl_FragColor = vec4(col, 1.0);
                }"""

    def initializeGL(self):
        self.context().aboutToBeDestroyed.connect(self.cleanup)
        self.initializeOpenGLFunctions()
        self.glClearColor(0, 0, 0, 0 if self._transparent else 1)

        self.program = QOpenGLShaderProgram()

        if self._core:
            self._vertex_shader = self.vertex_shader_source_core()
            self._fragment_shader = self.fragment_shader_source_core()
        else:
            self._vertex_shader = self.vertex_shader_source()
            self._fragment_shader = self.fragment_shader_source()

        self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, self._vertex_shader)
        self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, self._fragment_shader)
        self.program.bindAttributeLocation("vertex", 0)
        self.program.bindAttributeLocation("normal", 1)
        self.program.link()

        self.program.bind()
        self._proj_matrix_loc = self.program.uniformLocation("projMatrix")
        self._mv_matrix_loc = self.program.uniformLocation("mvMatrix")
        self._normal_matrix_loc = self.program.uniformLocation("normalMatrix")
        self._light_pos_loc = self.program.uniformLocation("lightPos")

        self.vao.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)

        self._logo_vbo.create()
        self._logo_vbo.bind()
        float_size = ctypes.sizeof(ctypes.c_float)
        self._logo_vbo.allocate(self.logo.const_data(), self.logo.count() * float_size)

        self.setup_vertex_attribs()

        self.camera.setToIdentity()
        self.camera.translate(0, 0, -1)

        self.program.setUniformValue(self._light_pos_loc, QVector3D(0, 0, 70))
        self.program.release()
        vao_binder = None

    def setup_vertex_attribs(self):
        self._logo_vbo.bind()
        f = QOpenGLContext.currentContext().functions()
        f.glEnableVertexAttribArray(0)
        f.glEnableVertexAttribArray(1)
        float_size = ctypes.sizeof(ctypes.c_float)

        null = VoidPtr(0)
        pointer = VoidPtr(3 * float_size)
        f.glVertexAttribPointer(0, 3, int(GL.GL_FLOAT), int(GL.GL_FALSE), 6 * float_size, null)
        f.glVertexAttribPointer(1, 3, int(GL.GL_FLOAT), int(GL.GL_FALSE), 6 * float_size, pointer)
        self._logo_vbo.release()

    def paintGL(self):
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.glEnable(GL.GL_DEPTH_TEST)
        self.glEnable(GL.GL_CULL_FACE)

        self.world.setToIdentity()
        self.world.rotate(180 - (self._x_rot / 16), 1, 0, 0)
        self.world.rotate(self._y_rot / 16, 0, 1, 0)
        self.world.rotate(self._z_rot / 16, 0, 0, 1)

        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        self.program.setUniformValue(self._proj_matrix_loc, self.proj)
        self.program.setUniformValue(self._mv_matrix_loc, self.camera * self.world)
        normal_matrix = self.world.normalMatrix()
        self.program.setUniformValue(self._normal_matrix_loc, normal_matrix)

        self.glDrawArrays(GL.GL_TRIANGLES, 0, self.logo.vertex_count())
        self.program.release()
        vao_binder = None

    def resizeGL(self, width, height):
        self.proj.setToIdentity()
        self.proj.perspective(45, width / height, 0.01, 100)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = ArgumentParser(description="hellogl2", formatter_class=RawTextHelpFormatter)
    parser.add_argument('--multisample', '-m', action='store_true',
                        help='Use Multisampling')
    parser.add_argument('--coreprofile', '-c', action='store_true',
                        help='Use Core Profile')
    parser.add_argument('--transparent', '-t', action='store_true',
                        help='Transparent Windows')
    options = parser.parse_args()

    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    if options.multisample:
        fmt.setSamples(4)
    if options.coreprofile:
        fmt.setVersion(3, 2)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)

    main_window = Window(options.transparent)
    main_window.resize(main_window.sizeHint())
    main_window.show()

    res = app.exec()
    sys.exit(res)
