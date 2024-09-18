# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QPoint, Slot
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy,
                               QPushButton)
from PySide6.QtWebEngineCore import QWebEngineNotification
from PySide6.QtGui import QPixmap, QMouseEvent


class NotificationPopup(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.notification = None
        self.m_icon, self.m_title, self.m_message = QLabel(), QLabel(), QLabel()
        self.setWindowFlags(Qt.WindowType.ToolTip)

        rootLayout = QHBoxLayout(self)
        rootLayout.addWidget(self.m_icon)

        bodyLayout = QVBoxLayout()
        rootLayout.addLayout(bodyLayout)

        titleLayout = QHBoxLayout()
        bodyLayout.addLayout(titleLayout)

        titleLayout.addWidget(self.m_title)
        titleLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding))

        close = QPushButton("Close")
        titleLayout.addWidget(close)
        close.clicked.connect(self.onClosed)

        bodyLayout.addWidget(self.m_message)
        self.adjustSize()

    def present(self, newNotification: QWebEngineNotification):
        if self.notification:
            self.notification.close()

        self.notification = newNotification

        self.m_title.setText("<b>" + self.notification.title() + "</b>")
        self.m_message.setText(self.notification.message())
        self.m_icon.setPixmap(QPixmap.fromImage(self.notification.icon())
                              .scaledToHeight(self.m_icon.height()))

        self.show()
        self.notification.show()

        self.notification.closed.connect(self.onClosed)
        QTimer.singleShot(10000, lambda: self.onClosed())

        self.move(self.parentWidget().mapToGlobal(self.parentWidget().rect().bottomRight()
                                                  - QPoint(self.width() + 10, self.height() + 10)))

    @Slot()
    def onClosed(self):
        self.hide()
        if self.notification:
            self.notification.close()
        self.notification = None

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        QWidget.mouseReleaseEvent(event)
        if self.notification and event.button() == Qt.MouseButton.LeftButton:
            self.notification.click()
            self.onClosed()
