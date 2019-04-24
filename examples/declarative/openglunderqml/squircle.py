#############################################################################
##
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
#############################################################################

from PySide6.QtCore import Property, QRunnable, Qt, Signal, Slot
from PySide6.QtQuick import QQuickItem, QQuickWindow

from squirclerenderer import SquircleRenderer


class CleanupJob(QRunnable):
    def __init__(self, renderer):
        super().__init__()
        self._renderer = renderer

    def run(self):
        del self._renderer


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

    def cleanup(self):
        del self._renderer
        self._renderer = None

    @Slot()
    def sync(self):
        if not self._renderer:
            self._renderer = SquircleRenderer()
            self.window().beforeRendering.connect(self._renderer.init, Qt.DirectConnection)
            self.window().beforeRenderPassRecording.connect(
                self._renderer.paint, Qt.DirectConnection
            )
        self._renderer.setViewportSize(self.window().size() * self.window().devicePixelRatio())
        self._renderer.setT(self._t)
        self._renderer.setWindow(self.window())

    def releaseResources(self):
        self.window().scheduleRenderJob(
            CleanupJob(self._renderer), QQuickWindow.BeforeSynchronizingStage
        )
        self._renderer = None

    t = Property(float, t, setT, notify=tChanged)
