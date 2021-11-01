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


from pathlib import Path
from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    Qt,
    QAbstractAnimation,
    QPropertyAnimation,
    Property,
)
from PySide6.QtGui import QPainter, QTransform, QPixmap
from PySide6.QtWidgets import QGraphicsView, QFrame, QGraphicsScene, QGraphicsPixmapItem
from math import pi, sin, cos
from blureffect import BlurEffect


class BlurPicker(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_index = 0
        self.m_animation = QPropertyAnimation(self, b"index")
        self.path = Path(__file__).resolve().parent

        self.setBackgroundBrush(QPixmap(self.path / "images" / "background.jpg"))
        self.setScene(QGraphicsScene(self))

        self.m_icons = []

        self.setup_scene()
        self.set_index(0)

        self.m_animation.setDuration(400)
        self.m_animation.setEasingCurve(QEasingCurve.InOutSine)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setFrameStyle(QFrame.NoFrame)

    def read_index(self) -> float:
        return self.m_index

    def set_index(self, index: float):
        self.m_index = index

        base_line = 0.0
        iconAngle = 2 * pi / len(self.m_icons)

        for i, icon in enumerate(self.m_icons):
            a = (i + self.m_index) * iconAngle
            xs = 170 * sin(a)
            ys = 100 * cos(a)
            pos = QPointF(xs, ys)
            pos = QTransform().rotate(-20).map(pos)
            pos -= QPointF(40, 40)
            icon.setPos(pos)
            base_line = max(base_line, ys)

            icon.graphicsEffect().set_base_line(base_line)

        self.scene().update()

    def setup_scene(self):
        self.scene().setSceneRect(-200, -120, 400, 240)

        names = [
            self.path / "images" / "accessories-calculator.png",
            self.path / "images" / "accessories-text-editor.png",
            self.path / "images" / "help-browser.png",
            self.path / "images" / "internet-group-chat.png",
            self.path / "images" / "internet-mail.png",
            self.path / "images" / "internet-web-browser.png",
            self.path / "images" / "office-calendar.png",
            self.path / "images" / "system-users.png",
        ]

        for name in names:
            pixmap = QPixmap(name)
            icon: QGraphicsPixmapItem = self.scene().addPixmap(pixmap)
            icon.setZValue(1)
            icon.setGraphicsEffect(BlurEffect(icon))
            self.m_icons.append(icon)

        bg: QGraphicsPixmapItem = self.scene().addPixmap(
            QPixmap(self.path / "images" / "background.jpg")
        )
        bg.setZValue(0)
        bg.setPos(-200, -150)

    def keyPressEvent(self, event):
        delta = 0
        if event.key() == Qt.Key_Left:
            delta = -1
        elif event.key() == Qt.Key_Right:
            delta = 1

        if self.m_animation.state() == QAbstractAnimation.Stopped and delta:
            self.m_animation.setEndValue(self.m_index + delta)
            self.m_animation.start()
            event.accept()

    def mousePressEvent(self, event):
        if event.position().x() > (self.width() / 2):
            delta = 1
        else:
            delta = -1

        if self.m_animation.state() == QAbstractAnimation.Stopped:
            self.m_animation.setEndValue(self.m_index + delta)
            self.m_animation.start()
            event.accept()

    index = Property(float, read_index, set_index)
