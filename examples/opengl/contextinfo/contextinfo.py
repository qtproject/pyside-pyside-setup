
#############################################################################
##
## Copyright (C) 2017 The Qt Company Ltd.
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

"""PySide6 port of the opengl/contextinfo example from Qt v5.x"""

from argparse import ArgumentParser, RawTextHelpFormatter
import numpy
import sys
from textwrap import dedent


from PySide6.QtCore import QCoreApplication, QLibraryInfo, QSize, QTimer, Qt
from PySide6.QtGui import (QMatrix4x4, QOpenGLContext, QSurfaceFormat, QWindow)
from PySide6.QtOpenGL import (QOpenGLBuffer, QOpenGLShader,
                              QOpenGLShaderProgram, QOpenGLVertexArrayObject)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMessageBox, QPlainTextEdit,
    QWidget)
from PySide6.support import VoidPtr
try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    message_box = QMessageBox(QMessageBox.Critical, "ContextInfo",
                             "PyOpenGL must be installed to run this example.",
                             QMessageBox.Close)
    message_box.setDetailedText("Run:\npip install PyOpenGL PyOpenGL_accelerate")
    message_box.exec()
    sys.exit(1)

vertex_shader_source_110 = dedent("""
    // version 110
    attribute highp vec4 posAttr;
    attribute lowp vec4 colAttr;
    varying lowp vec4 col;
    uniform highp mat4 matrix;
    void main() {
       col = colAttr;
       gl_Position = matrix * posAttr;
    }
    """)

fragment_shader_source_110 = dedent("""
    // version 110
    varying lowp vec4 col;
    void main() {
       gl_FragColor = col;
    }
    """)

vertex_shader_source = dedent("""
    // version 150
    in vec4 posAttr;
    in vec4 colAttr;
    out vec4 col;
    uniform mat4 matrix;
    void main() {
       col = colAttr;
       gl_Position = matrix * posAttr;
    }
    """)

fragment_shader_source = dedent("""
    // version 150
    in vec4 col;
    out vec4 fragColor;
    void main() {
       fragColor = col;
    }
    """)

vertices = numpy.array([0, 0.707, -0.5, -0.5, 0.5, -0.5], dtype=numpy.float32)
colors = numpy.array([1, 0, 0, 0, 1, 0, 0, 0, 1], dtype=numpy.float32)


def print_surface_format(surface_format):
    profile_name = 'core' if surface_format.profile() == QSurfaceFormat.CoreProfile else 'compatibility'
    major = surface_format.majorVersion()
    minor = surface_format.minorVersion()
    return f"{profile_name} version {major}.{minor}"


class RenderWindow(QWindow):
    def __init__(self, fmt):
        super().__init__()
        self.setSurfaceType(QWindow.OpenGLSurface)
        self.setFormat(fmt)
        self.context = QOpenGLContext(self)
        self.context.setFormat(self.requestedFormat())
        if not self.context.create():
            raise Exception("Unable to create GL context")
        self.program = None
        self.timer = None
        self.angle = 0

    def init_gl(self):
        self.program = QOpenGLShaderProgram(self)
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer()

        fmt = self.context.format()
        use_new_style_shader = fmt.profile() == QSurfaceFormat.CoreProfile
        # Try to handle 3.0 & 3.1 that do not have the core/compatibility profile
        # concept 3.2+ has. This may still fail since version 150 (3.2) is
        # specified in the sources but it's worth a try.
        if (fmt.renderableType() == QSurfaceFormat.OpenGL and fmt.majorVersion() == 3
            and fmt.minorVersion() <= 1):
            use_new_style_shader = not fmt.testOption(QSurfaceFormat.DeprecatedFunctions)

        vertex_shader = vertex_shader_source if use_new_style_shader else vertex_shader_source_110
        fragment_shader = fragment_shader_source if use_new_style_shader else fragment_shader_source_110
        if not self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, vertex_shader):
            log = self.program.log()
            raise Exception("Vertex shader could not be added: {log} ({vertexShader})")
        if not self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, fragment_shader):
            log = self.program.log()
            raise Exception(f"Fragment shader could not be added: {log} ({fragment_shader})")
        if not self.program.link():
            log = self.program.log()
            raise Exception(f"Could not link shaders: {log}")

        self._pos_attr = self.program.attributeLocation("posAttr")
        self._col_attr = self.program.attributeLocation("colAttr")
        self._matrix_uniform = self.program.uniformLocation("matrix")

        self.vbo.create()
        self.vbo.bind()
        self._vertices_data = vertices.tobytes()
        self._colors_data = colors.tobytes()
        vertices_size = 4 * vertices.size
        colors_size = 4 * colors.size
        self.vbo.allocate(VoidPtr(self._vertices_data), vertices_size + colors_size)
        self.vbo.write(vertices_size, VoidPtr(self._colors_data), colors_size)
        self.vbo.release()

        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)
        if self.vao.isCreated():  # have VAO support, use it
            self.setup_vertex_attribs()

    def setup_vertex_attribs(self):
        self.vbo.bind()
        self.program.setAttributeBuffer(self._pos_attr, GL.GL_FLOAT, 0, 2)
        self.program.setAttributeBuffer(self._col_attr, GL.GL_FLOAT, 4 * vertices.size, 3)
        self.program.enableAttributeArray(self._pos_attr)
        self.program.enableAttributeArray(self._col_attr)
        self.vbo.release()

    def exposeEvent(self, event):
        if self.isExposed():
            self.render()
            if self.timer is None:
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.slot_timer)
            if not self.timer.isActive():
                self.timer.start(10)
        else:
            if self.timer and self.timer.isActive():
                self.timer.stop()

    def render(self):
        if not self.context.makeCurrent(self):
            raise Exception("makeCurrent() failed")
        functions = self.context.functions()
        if self.program is None:
            functions.glEnable(GL.GL_DEPTH_TEST)
            functions.glClearColor(0, 0, 0, 1)
            self.init_gl()

        retina_scale = self.devicePixelRatio()
        functions.glViewport(0, 0, self.width() * retina_scale,
                             self.height() * retina_scale)
        functions.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.program.bind()
        matrix = QMatrix4x4()
        matrix.perspective(60, 4 / 3, 0.1, 100)
        matrix.translate(0, 0, -2)
        matrix.rotate(self.angle, 0, 1, 0)
        self.program.setUniformValue(self._matrix_uniform, matrix)

        if self.vao.isCreated():
            self.vao.bind()
        else:  # no VAO support, set the vertex attribute arrays now
            self.setup_vertex_attribs()

        functions.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

        self.vao.release()
        self.program.release()

        # swapInterval is 1 by default which means that swapBuffers() will (hopefully) block
        # and wait for vsync.
        self.context.swapBuffers(self)
        self.context.doneCurrent()

    def slot_timer(self):
        self.render()
        self.angle += 1

    def glInfo(self):
        if not self.context.makeCurrent(self):
            raise Exception("makeCurrent() failed")
        functions = self.context.functions()
        gl_vendor = functions.glGetString(GL.GL_VENDOR)
        gl_renderer = functions.glGetString(GL.GL_RENDERER)
        gl_version = functions.glGetString(GL.GL_VERSION)
        gl_lang_version = functions.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)
        context_surface_format = print_surface_format(self.context.format())
        surface_format = print_surface_format(self.format())

        text = ("Vendor: {gl_vendor}\n"
                "Renderer: {gl_renderer}\n"
                "Version: {gl_version}\n"
                "Shading language: {gl_lang_version}\n"
                "Context Format: {context_surface_format}\n\n"
                "Surface Format: {surface_format}")
        self.context.doneCurrent()
        return text


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        h_box_layout = QHBoxLayout(self)
        self._plain_text_edit = QPlainTextEdit()
        self._plain_text_edit.setMinimumWidth(400)
        self._plain_text_edit.setReadOnly(True)
        h_box_layout.addWidget(self._plain_text_edit)
        self._render_window = RenderWindow(QSurfaceFormat())
        container = QWidget.createWindowContainer(self._render_window)
        container.setMinimumSize(QSize(400, 400))
        h_box_layout.addWidget(container)

    def update_description(self):
        build = QLibraryInfo.build()
        gl = self._render_window.glInfo()
        text = f"{build}\n\nPython {sys.version}\n\n{gl}"
        self._plain_text_edit.setPlainText(text)


if __name__ == '__main__':
    parser = ArgumentParser(description="contextinfo", formatter_class=RawTextHelpFormatter)
    parser.add_argument('--gles', '-g', action='store_true',
                        help='Use OpenGL ES')
    parser.add_argument('--software', '-s', action='store_true',
                        help='Use Software OpenGL')
    parser.add_argument('--desktop', '-d', action='store_true',
                        help='Use Desktop OpenGL')
    options = parser.parse_args()
    if options.gles:
        QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)
    elif options.software:
        QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
    elif options.desktop:
        QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.update_description()
    sys.exit(app.exec())
