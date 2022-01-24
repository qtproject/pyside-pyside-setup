#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
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


from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QMutexLocker, QSize, QThread, Slot, Signal

from renderer import Renderer


class GLWidget(QOpenGLWidget):

    render_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.aboutToCompose.connect(self.on_about_to_compose)
        self.frameSwapped.connect(self.on_frame_swapped)
        self.aboutToResize.connect(self.on_about_to_resize)
        self.resized.connect(self.on_resized)

        self._thread = QThread()
        self._renderer = Renderer(self)
        self._renderer.moveToThread(self._thread)
        self._thread.finished.connect(self._renderer.deleteLater)

        self.render_requested.connect(self._renderer.render)
        self._renderer.context_wanted.connect(self.grab_context)

        self._thread.start()

    def stop_rendering(self):
        self._renderer.prepare_exit()
        self._thread.quit()
        self._thread.wait()
        self._thread = None
        self._renderer = None

    def closeEvent(self, event):
        self.stop_rendering()
        event.accept()

    def paintEvent(self, event):
        pass

    def sizeHint(self):
        return QSize(200, 200)

    @Slot()
    def on_about_to_compose(self):
        # We are on the gui thread here. Composition is about to
        # begin. Wait until the render thread finishes.
        self._renderer.lock_renderer()

    @Slot()
    def on_frame_swapped(self):
        self._renderer.unlock_renderer()
        # Assuming a blocking swap, our animation is driven purely by the
        # vsync in self example.
        self.render_requested.emit()

    @Slot()
    def on_about_to_resize(self):
        self._renderer.lock_renderer()

    @Slot()
    def on_resized(self):
        self._renderer.unlock_renderer()

    def grab_context(self):
        if not self._renderer:
            return
        self._renderer.lock_renderer()
        with QMutexLocker(self._renderer.grab_mutex()):
            self.context().moveToThread(self._thread)
            self._renderer.grab_condition().wakeAll()
            self._renderer.unlock_renderer()
