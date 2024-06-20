# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations


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

    @Slot()
    def grab_context(self):
        if not self._renderer:
            return
        self._renderer.lock_renderer()
        with QMutexLocker(self._renderer.grab_mutex()):
            self.context().moveToThread(self._thread)
            self._renderer.grab_condition().wakeAll()
            self._renderer.unlock_renderer()
