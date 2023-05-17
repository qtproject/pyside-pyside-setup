# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit test for QOpenGLContext, QOpenGLTexture, QOpenGLWindow and related classes'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtGui import (QColor, QGuiApplication, QImage, QOpenGLContext,
    QSurfaceFormat)
from PySide6.QtOpenGL import (QOpenGLTexture, QOpenGLWindow, QOpenGLVersionProfile,
                              QOpenGLVersionFunctionsFactory)


try:
    from OpenGL import GL
except ImportError:
    print("Skipping test due to missing OpenGL module")
    sys.exit(0)


class OpenGLWindow(QOpenGLWindow):
    def __init__(self):
        super().__init__()

        self.m_functions = None
        self.m_texture = None
        self.visibleChanged.connect(self.slotVisibleChanged)

    def slotVisibleChanged(self, visible):
        if not visible and self.m_texture is not None and self.context().makeCurrent(self):
            self.m_texture = None
            self.context().doneCurrent()

    def initializeGL(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(1, 3)
        profile.setProfile(QSurfaceFormat.CompatibilityProfile)
        self.m_functions = QOpenGLVersionFunctionsFactory.get(profile)
        self.m_functions.initializeOpenGLFunctions()

        print("GL_MAX_LIGHTS=", self.m_functions.glGetIntegerv(GL.GL_MAX_LIGHTS))
        image = QImage(QSize(200, 200), QImage.Format_RGBA8888)
        image.fill(QColor(Qt.red))
        self.m_texture = QOpenGLTexture(image)

    def paintGL(self):
        self.m_functions.glMatrixMode(GL.GL_MODELVIEW)
        self.m_functions.glLoadIdentity()

        self.m_functions.glMatrixMode(GL.GL_PROJECTION)
        self.m_functions.glLoadIdentity()
        self.m_functions.glOrtho(0, 1, 1, 0, -1, 1)

        self.m_functions.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.m_functions.glEnable(GL.GL_TEXTURE_2D)
        self.m_texture.bind()

        d = 0.5
        self.m_functions.glBegin(GL.GL_QUADS)
        self.m_functions.glTexCoord2f(0, 0)
        self.m_functions.glVertex2f(0, 0)
        self.m_functions.glTexCoord2f(d, 0)
        self.m_functions.glVertex2f(d, 0)
        self.m_functions.glTexCoord2f(d, d)
        self.m_functions.glVertex2f(d, d)
        self.m_functions.glTexCoord2f(0, d)
        self.m_functions.glVertex2f(0, d)
        self.m_functions.glEnd()
        self.m_texture.release()

    def resizeGL(self, w, h):
        self.m_functions.glViewport(0, 0, self.width(), self.height())


class QOpenGLWindowTest(UsesQApplication):
    # On macOS, glClear(), glViewport() are rejected due to GLbitfield/GLint not being resolved properly
    def test(self):
        openGlWindow = OpenGLWindow()
        openGlWindow.resize(640, 480)
        openGlWindow.show()
        QTimer.singleShot(100, openGlWindow.close)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
