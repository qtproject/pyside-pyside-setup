# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QPalette
from PySide6.QtCore import Qt, QOperatingSystemVersion, Slot


class VideoWidget(QVideoWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
        self.setPalette(p)
        if QOperatingSystemVersion.currentType() != QOperatingSystemVersion.OSType.Android:
            self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)

    def keyPressEvent(self, event):
        key = event.key()
        if (key == Qt.Key.Key_Escape or key == Qt.Key.Key_Back) and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        elif key == Qt.Key.Key_Enter and event.modifiers() & Qt.Key.Key_Alt:
            self.setFullScreen(not self.isFullScreen())
            event.accept()
        else:
            super().keyPressEvent(event)

    @Slot()
    def switchToFullScreen(self):
        self.setFullScreen(True)

    def mouseDoubleClickEvent(self, event):
        self.setFullScreen(not self.isFullScreen())
        event.accept()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
