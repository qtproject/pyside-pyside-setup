# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the opengl/textures example from Qt v6.x showing the use
   of legacy OpenGL functions with QOpenGLVersionFunctionsFactory."""

import sys
from PySide6.QtCore import QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QImage, QSurfaceFormat
from PySide6.QtWidgets import QApplication, QGridLayout, QMessageBox, QWidget
from PySide6.QtOpenGL import (QOpenGLTexture, QOpenGLVersionFunctionsFactory,
                              QOpenGLVersionProfile)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    messageBox = QMessageBox(QMessageBox.Critical, "OpenGL textures",
                             "PyOpenGL must be installed to run this example.",
                             QMessageBox.Close)
    messageBox.setDetailedText("Run:\npip install PyOpenGL PyOpenGL_accelerate")
    messageBox.exec()
    sys.exit(1)

import textures_rc


class GLWidget(QOpenGLWidget):
    sharedObject = 0
    refCount = 0

    coords = (
        ( ( +1, -1, -1 ), ( -1, -1, -1 ), ( -1, +1, -1 ), ( +1, +1, -1 ) ),
        ( ( +1, +1, -1 ), ( -1, +1, -1 ), ( -1, +1, +1 ), ( +1, +1, +1 ) ),
        ( ( +1, -1, +1 ), ( +1, -1, -1 ), ( +1, +1, -1 ), ( +1, +1, +1 ) ),
        ( ( -1, -1, -1 ), ( -1, -1, +1 ), ( -1, +1, +1 ), ( -1, +1, -1 ) ),
        ( ( +1, -1, +1 ), ( -1, -1, +1 ), ( -1, -1, -1 ), ( +1, -1, -1 ) ),
        ( ( -1, -1, +1 ), ( +1, -1, +1 ), ( +1, +1, +1 ), ( -1, +1, +1 ) )
    )

    clicked = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        self.clearColor = Qt.black
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.clearColor = QColor()
        self.lastPos = QPoint()
        self.funcs = None

    def freeGLResources(self):
        GLWidget.refCount -= 1
        if GLWidget.refCount == 0:
            self.makeCurrent()
            self.funcs.glDeleteLists(self.__class__.sharedObject, 1)

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(200, 200)

    def rotateBy(self, xAngle, yAngle, zAngle):
        self.xRot = (self.xRot + xAngle) % 5760
        self.yRot = (self.yRot + yAngle) % 5760
        self.zRot = (self.zRot + zAngle) % 5760
        self.update()

    def setClearColor(self, color):
        self.clearColor = color
        self.update()

    def initializeGL(self):
        profile = QOpenGLVersionProfile()
        profile.setVersion(3, 2)
        profile.setProfile(QSurfaceFormat.CompatibilityProfile)
        self.funcs = QOpenGLVersionFunctionsFactory.get(profile)
        self.funcs.initializeOpenGLFunctions()

        if not GLWidget.sharedObject:
            self.textures = []
            for i in range(6):
                image = QImage(f":/images/side{i + 1}.png")
                self.textures.append(QOpenGLTexture(image))
            GLWidget.sharedObject = self.makeObject()
        GLWidget.refCount += 1

        self.funcs.glEnable(GL.GL_DEPTH_TEST)
        self.funcs.glEnable(GL.GL_CULL_FACE)
        self.funcs.glEnable(GL.GL_TEXTURE_2D)

    def paintGL(self):
        self.funcs.glClearColor(self.clearColor.red(), self.clearColor.green(),
                                self.clearColor.blue(), 1)
        self.funcs.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.funcs.glLoadIdentity()
        self.funcs.glTranslated(0.0, 0.0, -10.0)
        self.funcs.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self.funcs.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self.funcs.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self.funcs.glCallList(GLWidget.sharedObject)

    def resizeGL(self, width, height):
        side = min(width, height)
        x = int((width - side) / 2)
        y = int((height - side) / 2)
        self.funcs.glViewport(x, y, side, side)

        self.funcs.glMatrixMode(GL.GL_PROJECTION)
        self.funcs.glLoadIdentity()
        self.funcs.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        self.funcs.glMatrixMode(GL.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        dx = pos.x() - self.lastPos.x()
        dy = pos.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.rotateBy(8 * dy, 8 * dx, 0)
        elif event.buttons() & Qt.RightButton:
            self.rotateBy(8 * dy, 0, 8 * dx)

        self.lastPos = pos

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def makeObject(self):
        dlist = self.funcs.glGenLists(1)
        self.funcs.glNewList(dlist, GL.GL_COMPILE)

        for i in range(6):
            self.textures[i].bind()

            self.funcs.glBegin(GL.GL_QUADS)
            for j in range(4):
                tx = {False: 0, True: 1}[j == 0 or j == 3]
                ty = {False: 0, True: 1}[j == 0 or j == 1]
                self.funcs.glTexCoord2d(tx, ty)
                x = 0.2 * GLWidget.coords[i][j][0]
                y = 0.2 * GLWidget.coords[i][j][1]
                z = 0.2 * GLWidget.coords[i][j][2]
                self.funcs.glVertex3d(x, y, z)

            self.funcs.glEnd()

        self.funcs.glEndList()
        return dlist


class Window(QWidget):
    NumRows = 2
    NumColumns = 3

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        mainLayout = QGridLayout(self)
        self.glWidgets = []

        for i in range(Window.NumRows):
            self.glWidgets.append([])
            for j in range(Window.NumColumns):
                self.glWidgets[i].append(None)

        hue_div = (Window.NumRows * Window.NumColumns - 1)
        for i in range(Window.NumRows):
            for j in range(Window.NumColumns):
                clearColor = QColor()
                hue = ((i * Window.NumColumns) + j) * 255 / hue_div
                clearColor.setHsv(hue, 255, 63)

                glw = GLWidget(self)
                self.glWidgets[i][j] = glw
                glw.setClearColor(clearColor)
                glw.rotateBy(+42 * 16, +42 * 16, -21 * 16)
                mainLayout.addWidget(glw, i, j)

                glw.clicked.connect(self.setCurrentGlWidget)
                qApp.lastWindowClosed.connect(glw.freeGLResources)

        self.currentGlWidget = self.glWidgets[0][0]

        timer = QTimer(self)
        timer.timeout.connect(self.rotateOneStep)
        timer.start(20)

        self.setWindowTitle(self.tr("Textures"))

    def setCurrentGlWidget(self):
        self.currentGlWidget = self.sender()

    def rotateOneStep(self):
        if self.currentGlWidget:
            self.currentGlWidget.rotateBy(+2 * 16, +2 * 16, -1 * 16)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
