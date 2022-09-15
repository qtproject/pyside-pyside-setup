# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import Property, QRunnable, Qt, Signal, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickItem, QQuickWindow

from squirclerenderer import SquircleRenderer

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "OpenGLUnderQML"
QML_IMPORT_MAJOR_VERSION = 1


class CleanupJob(QRunnable):
    def __init__(self, renderer):
        super().__init__()
        self._renderer = renderer

    def run(self):
        del self._renderer


@QmlElement
class Squircle(QQuickItem):

    tChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = 0.0
        self._renderer = None
        self.windowChanged.connect(self.handleWindowChanged)

    def t(self):
        return self._t

    def setT(self, value):
        if self._t == value:
            return
        self._t = value
        self.tChanged.emit()
        if self.window():
            self.window().update()

    @Slot(QQuickWindow)
    def handleWindowChanged(self, win):
        if win:
            win.beforeSynchronizing.connect(self.sync, type=Qt.DirectConnection)
            win.sceneGraphInvalidated.connect(self.cleanup, type=Qt.DirectConnection)
            win.setColor(Qt.black)
            self.sync()

    @Slot()
    def cleanup(self):
        del self._renderer
        self._renderer = None

    @Slot()
    def sync(self):
        window = self.window()
        if not self._renderer:
            self._renderer = SquircleRenderer()
            window.beforeRendering.connect(self._renderer.init, Qt.DirectConnection)
            window.beforeRenderPassRecording.connect(
                self._renderer.paint, Qt.DirectConnection
            )
        self._renderer.setViewportSize(window.size() * window.devicePixelRatio())
        self._renderer.setT(self._t)
        self._renderer.setWindow(window)

    def releaseResources(self):
        self.window().scheduleRenderJob(
            CleanupJob(self._renderer), QQuickWindow.BeforeSynchronizingStage
        )
        self._renderer = None

    t = Property(float, t, setT, notify=tChanged)
