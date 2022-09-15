# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import numpy
from pathlib import Path
import sys
import weakref
from OpenGL.GL import (GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER,
                       GL_NEAREST, GL_RGBA, GL_TEXTURE_2D, GL_UNSIGNED_BYTE)

from PySide6.QtGui import (QMatrix4x4, QMouseEvent, QOffscreenSurface,
                           QOpenGLContext, QOpenGLFunctions, QScreen, QSurface,
                           QSurfaceFormat, QWindow)
from PySide6.QtOpenGL import (QOpenGLFramebufferObject, QOpenGLTexture,
                              QOpenGLShaderProgram, QOpenGLVertexArrayObject,
                              QOpenGLBuffer)
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import (QQuickGraphicsDevice,
                             QQuickItem, QQuickRenderControl,
                             QQuickRenderTarget, QQuickWindow)
from PySide6.QtCore import QCoreApplication, QTimer, QUrl, Slot
from shiboken6 import VoidPtr

from cuberenderer import CubeRenderer


class RenderControl(QQuickRenderControl):
    def __init__(self, window=None):
        super().__init__()
        self._window = window

    def renderWindow(self, offset):
        return self._window()  # Dereference the weak reference


class WindowSingleThreaded(QWindow):

    def __init__(self):
        super().__init__()
        self.m_rootItem = None
        self.m_device = None
        self.m_texture_ids = numpy.array([0], dtype=numpy.uint32)

        self.m_quickInitialized = False
        self.m_quickReady = False
        self.m_dpr = 0
        self.m_status_conn_id = None
        self.setSurfaceType(QSurface.OpenGLSurface)

        format = QSurfaceFormat()
        # Qt Quick may need a depth and stencil buffer. Always make sure these
        # are available.
        format.setDepthBufferSize(16)
        format.setStencilBufferSize(8)
        self.setFormat(format)

        self.m_context = QOpenGLContext()
        self.m_context.setFormat(format)
        self.m_context.create()

        self.m_offscreenSurface = QOffscreenSurface()
        # Pass m_context.format(), not format. Format does not specify and
        # color buffer sizes, while the context, that has just been created,
        # reports a format that has these values filled in. Pass self to the
        # offscreen surface to make sure it will be compatible with the
        # context's configuration.
        self.m_offscreenSurface.setFormat(self.m_context.format())
        self.m_offscreenSurface.create()

        self.m_cubeRenderer = CubeRenderer(self.m_offscreenSurface)

        self.m_renderControl = RenderControl(weakref.ref(self))

        # Create a QQuickWindow that is associated with out render control.
        # Note that this window never gets created or shown, meaning that
        # will never get an underlying native (platform) window.
        self.m_quickWindow = QQuickWindow(self.m_renderControl)

        # Create a QML engine.
        self.m_qmlEngine = QQmlEngine()
        if not self.m_qmlEngine.incubationController():
            c = self.m_quickWindow.incubationController()
            self.m_qmlEngine.setIncubationController(c)

        # When Quick says there is a need to render, we will not render
        # immediately. Instead, a timer with a small interval is used
        # to get better performance.
        self.m_updateTimer = QTimer()
        self.m_updateTimer.setSingleShot(True)
        self.m_updateTimer.setInterval(5)
        self.m_updateTimer.timeout.connect(self.render)

        # Now hook up the signals. For simplicy we don't differentiate between
        # renderRequested (only render is needed, no sync) and sceneChanged
        # (polish and sync is needed too).
        self.m_quickWindow.sceneGraphInitialized.connect(self.createTexture)
        self.m_quickWindow.sceneGraphInvalidated.connect(self.destroyTexture)
        self.m_renderControl.renderRequested.connect(self.requestUpdate)
        self.m_renderControl.sceneChanged.connect(self.requestUpdate)

        # Just recreating the texture on resize is not sufficient, when moving
        # between screens with different devicePixelRatio the QWindow size may
        # remain the same but the texture dimension is to change regardless.
        self.screenChanged.connect(self.handleScreenChange)

    def __del__(self):
        # Make sure the context is current while doing cleanup. Note that
        # we use the offscreen surface here because passing 'self' at self
        # point is not safe: the underlying platform window may already be
        # destroyed. To avoid all the trouble, use another surface that is
        # valid for sure.
        self.m_context.makeCurrent(self.m_offscreenSurface)

        del self.m_qmlComponent
        del self.m_qmlEngine
        del self.m_quickWindow
        del self.m_renderControl

        if self.texture_id():
            self.m_context.functions().glDeleteTextures(1, self.m_texture_ids)

        self.m_context.doneCurrent()

    def texture_id(self):
        return self.m_texture_ids[0]

    def set_texture_id(self, texture_id):
        self.m_texture_ids[0] = texture_id

    @Slot()
    def createTexture(self):
        # The scene graph has been initialized. It is now time to create a
        # texture and associate it with the QQuickWindow.
        self.m_dpr = self.devicePixelRatio()
        self.m_textureSize = self.size() * self.m_dpr
        f = self.m_context.functions()
        f.glGenTextures(1, self.m_texture_ids)
        f.glBindTexture(GL_TEXTURE_2D, self.texture_id())

        f.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        f.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        null = VoidPtr(0)
        f.glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.m_textureSize.width(),
                       self.m_textureSize.height(), 0,
                       GL_RGBA, GL_UNSIGNED_BYTE, null)
        target = QQuickRenderTarget.fromOpenGLTexture(self.texture_id(),
                                                      self.m_textureSize)
        self.m_quickWindow.setRenderTarget(target)

    @Slot()
    def destroyTexture(self):
        self.m_context.functions().glDeleteTextures(1, self.m_texture_ids)
        self.set_texture_id(0)

    @Slot()
    def render(self):
        if not self.m_context.makeCurrent(self.m_offscreenSurface):
            return

        # Polish, synchronize and render the next frame (into our texture).
        # In this example everything happens on the same thread and therefore
        # all three steps are performed in succession from here. In a threaded
        # setup the render() call would happen on a separate thread.
        self.m_renderControl.beginFrame()
        self.m_renderControl.polishItems()
        self.m_renderControl.sync()
        self.m_renderControl.render()
        self.m_renderControl.endFrame()

        QOpenGLFramebufferObject.bindDefault()
        self.m_context.functions().glFlush()

        self.m_quickReady = True

        # Get something onto the screen.
        texture_id = self.texture_id() if self.m_quickReady else 0
        self.m_cubeRenderer.render(self, self.m_context, texture_id)

    def requestUpdate(self):
        if not self.m_updateTimer.isActive():
            self.m_updateTimer.start()

    def run(self):
        if self.m_status_conn_id:
            self.m_qmlComponent.statusChanged.disconnect(self.m_status_conn_id)
            self.m_status_conn_id = None

        if self.m_qmlComponent.isError():
            for error in self.m_qmlComponent.errors():
                print(error.url().toString(), error.line(), error.toString())
            return

        self.m_rootItem = self.m_qmlComponent.create()
        if self.m_qmlComponent.isError():
            for error in self.m_qmlComponent.errors():
                print(error.url().toString(), error.line(), error.toString())
            return

        if not self.m_rootItem:
            print("run: Not a QQuickItem")
            del self.m_rootItem

        # The root item is ready. Associate it with the window.
        self.m_rootItem.setParentItem(self.m_quickWindow.contentItem())

        # Update item and rendering related geometries.
        self.updateSizes()

        # Initialize the render control and our OpenGL resources.
        self.m_context.makeCurrent(self.m_offscreenSurface)
        self.m_device = QQuickGraphicsDevice.fromOpenGLContext(self.m_context)
        self.m_quickWindow.setGraphicsDevice(self.m_device)
        self.m_renderControl.initialize()
        self.m_quickInitialized = True

    def updateSizes(self):
        # Behave like SizeRootObjectToView.
        w = self.width()
        h = self.height()
        self.m_rootItem.setWidth(w)
        self.m_rootItem.setHeight(h)
        self.m_quickWindow.setGeometry(0, 0, w, h)
        self.m_cubeRenderer.resize(w, h)

    def startQuick(self, filename):
        url = QUrl.fromLocalFile(filename)
        self.m_qmlComponent = QQmlComponent(self.m_qmlEngine, url)
        if self.m_qmlComponent.isLoading():
            self.m_status_conn_id = self.m_qmlComponent.statusChanged.connect(self.run)
        else:
            self.run()

    def exposeEvent(self, event):
        if self.isExposed() and not self.m_quickInitialized:
            texture_id = self.texture_id() if self.m_quickReady else 0
            self.m_cubeRenderer.render(self, self.m_context, texture_id)
            qml_file = Path(__file__).parent / "demo.qml"
            self.startQuick(qml_file)

    def resizeTexture(self):
        if self.m_rootItem and self.m_context.makeCurrent(self.m_offscreenSurface):
            self.m_context.functions().glDeleteTextures(1, self.m_texture_ids)
            self.set_texture_id(0)
            self.createTexture()
            self.m_context.doneCurrent()
            self.updateSizes()
            self.render()

    def resizeEvent(self, event):
        # If self is a resize after the scene is up and running, recreate the
        # texture and the Quick item and scene.
        if (self.texture_id()
            and self.m_textureSize != self.size() * self.devicePixelRatio()):
            self.resizeTexture()

    @Slot()
    def handleScreenChange(self):
        if self.m_dpr != self.devicePixelRatio():
            self.resizeTexture()

    def mousePressEvent(self, e):
        # Use the constructor taking position and globalPosition. That puts
        # position into the event's position and scenePosition, and
        # globalPosition into the event's globalPosition. This way the
        # scenePosition in `e` is ignored and is replaced by position.
        # This is necessary because QQuickWindow thinks of itself as
        # a top-level window always.
        mappedEvent = QMouseEvent(e.type(), e.position(), e.globalPosition(),
                                  e.button(), e.buttons(), e.modifiers())
        QCoreApplication.sendEvent(self.m_quickWindow, mappedEvent)

    def mouseReleaseEvent(self, e):
        mappedEvent = QMouseEvent(e.type(), e.position(), e.globalPosition(),
                                  e.button(), e.buttons(), e.modifiers())
        QCoreApplication.sendEvent(self.m_quickWindow, mappedEvent)
