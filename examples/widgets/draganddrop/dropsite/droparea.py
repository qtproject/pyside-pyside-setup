# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QMimeData, Qt, Slot, Signal
from PySide6.QtGui import QPalette, QPixmap
from PySide6.QtWidgets import QFrame, QLabel


class DropArea(QLabel):

    changed = Signal(QMimeData)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.clear()

    def dragEnterEvent(self, event):
        self.setText("<drop content>")
        self.setBackgroundRole(QPalette.Highlight)

        event.acceptProposedAction()
        self.changed.emit(event.mimeData())

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()

        if mime_data.hasImage():
            self.setPixmap(QPixmap(mime_data.imageData()))
        elif mime_data.hasFormat("text/markdown"):
            self.setText(mime_data.data("text/markdown"))
            self.setTextFormat(Qt.MarkdownText)
        elif mime_data.hasHtml():
            self.setText(mime_data.html())
            self.setTextFormat(Qt.RichText)
        elif mime_data.hasText():
            self.setText(mime_data.text())
            self.setTextFormat(Qt.PlainText)
        elif mime_data.hasUrls():
            url_list = mime_data.urls()
            text = ""
            for i in range(0, min(len(url_list), 32)):
                text += url_list[i].path() + "\n"
            self.setText(text)
        else:
            self.setText("Cannot display data")

        self.setBackgroundRole(QPalette.Dark)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.clear()
        event.accept()

    @Slot()
    def clear(self):
        self.setText("<drop content>")
        self.setBackgroundRole(QPalette.Dark)

        self.changed.emit(None)
