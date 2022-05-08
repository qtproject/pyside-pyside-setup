#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
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
        self.setWindowFlags(Qt.ToolTip)

        rootLayout = QHBoxLayout(self)
        rootLayout.addWidget(self.m_icon)

        bodyLayout = QVBoxLayout()
        rootLayout.addLayout(bodyLayout)

        titleLayout = QHBoxLayout()
        bodyLayout.addLayout(titleLayout)

        titleLayout.addWidget(self.m_title)
        titleLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding))

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

        self.move(self.parentWidget().mapToGlobal(self.parentWidget().rect().bottomRight() -
                  QPoint(self.width() + 10, self.height() + 10)))

    @Slot()
    def onClosed(self):
        self.hide()
        if self.notification:
            self.notification.close()
        self.notification = None

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        QWidget.mouseReleaseEvent(event)
        if self.notification and event.button() == Qt.LeftButton:
            self.notification.click()
            self.onClosed()
