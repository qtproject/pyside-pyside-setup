
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
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

import math
import sys

from PySide6.QtCore import (QLineF, QPointF, QRandomGenerator, QRectF, QTimer,
                            Qt)
from PySide6.QtGui import (QBrush, QColor, QPainter, QPainterPath, QPixmap,
                           QPolygonF, QTransform)
from PySide6.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene,
                               QGraphicsView)

import mice_rc


def random(boundary):
    return QRandomGenerator.global_().bounded(boundary)


class Mouse(QGraphicsItem):
    PI = math.pi
    TWO_PI = 2.0 * PI

    # Create the bounding rectangle once.
    adjust = 0.5
    BOUNDING_RECT = QRectF(-20 - adjust, -22 - adjust, 40 + adjust,
            83 + adjust)

    def __init__(self):
        super().__init__()

        self.angle = 0.0
        self.speed = 0.0
        self._mouse_eye_direction = 0.0
        self.color = QColor(random(256), random(256), random(256))

        self.setTransform(QTransform().rotate(random(360 * 16)))

    @staticmethod
    def normalize_angle(angle):
        while angle < 0:
            angle += Mouse.TWO_PI
        while angle > Mouse.TWO_PI:
            angle -= Mouse.TWO_PI
        return angle

    def boundingRect(self):
        return Mouse.BOUNDING_RECT

    def shape(self):
        path = QPainterPath()
        path.addRect(-10, -20, 20, 40)
        return path

    def paint(self, painter, option, widget):
        # Body.
        painter.setBrush(self.color)
        painter.drawEllipse(-10, -20, 20, 40)

        # Eyes.
        painter.setBrush(Qt.white)
        painter.drawEllipse(-10, -17, 8, 8)
        painter.drawEllipse(2, -17, 8, 8)

        # Nose.
        painter.setBrush(Qt.black)
        painter.drawEllipse(QRectF(-2, -22, 4, 4))

        # Pupils.
        painter.drawEllipse(QRectF(-8.0 + self._mouse_eye_direction, -17, 4, 4))
        painter.drawEllipse(QRectF(4.0 + self._mouse_eye_direction, -17, 4, 4))

        # Ears.
        if self.scene().collidingItems(self):
            painter.setBrush(Qt.red)
        else:
            painter.setBrush(Qt.darkYellow)

        painter.drawEllipse(-17, -12, 16, 16)
        painter.drawEllipse(1, -12, 16, 16)

        # Tail.
        path = QPainterPath(QPointF(0, 20))
        path.cubicTo(-5, 22, -5, 22, 0, 25)
        path.cubicTo(5, 27, 5, 32, 0, 30)
        path.cubicTo(-5, 32, -5, 42, 0, 35)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    def advance(self, phase):
        if not phase:
            return
        # Don't move too far away.
        line_to_center = QLineF(QPointF(0, 0), self.mapFromScene(0, 0))
        if line_to_center.length() > 150:
            angle_to_center = math.acos(line_to_center.dx() / line_to_center.length())
            if line_to_center.dy() < 0:
                angle_to_center = Mouse.TWO_PI - angle_to_center
            angle_to_center = Mouse.normalize_angle((Mouse.PI - angle_to_center) + Mouse.PI / 2)

            if angle_to_center < Mouse.PI and angle_to_center > Mouse.PI / 4:
                # Rotate left.
                self.angle += [-0.25, 0.25][self.angle < -Mouse.PI / 2]
            elif angle_to_center >= Mouse.PI and angle_to_center < (Mouse.PI + Mouse.PI / 2 + Mouse.PI / 4):
                # Rotate right.
                self.angle += [-0.25, 0.25][self.angle < Mouse.PI / 2]
        elif math.sin(self.angle) < 0:
            self.angle += 0.25
        elif math.sin(self.angle) > 0:
            self.angle -= 0.25

        # Try not to crash with any other mice.
        danger_mice = self.scene().items(QPolygonF([self.mapToScene(0, 0),
                                                    self.mapToScene(-30, -50),
                                                    self.mapToScene(30, -50)]))

        for item in danger_mice:
            if item is self:
                continue

            line_to_mouse = QLineF(QPointF(0, 0), self.mapFromItem(item, 0, 0))
            angle_to_mouse = math.acos(line_to_mouse.dx() / line_to_mouse.length())
            if line_to_mouse.dy() < 0:
                angle_to_mouse = Mouse.TWO_PI - angle_to_mouse
            angle_to_mouse = Mouse.normalize_angle((Mouse.PI - angle_to_mouse) + Mouse.PI / 2)

            if angle_to_mouse >= 0 and angle_to_mouse < Mouse.PI / 2:
                # Rotate right.
                self.angle += 0.5
            elif angle_to_mouse <= Mouse.TWO_PI and angle_to_mouse > (Mouse.TWO_PI - Mouse.PI / 2):
                # Rotate left.
                self.angle -= 0.5

        # Add some random movement.
        if len(danger_mice) > 1 and random(10) == 0:
            if random(2) != 0:
                self.angle += random(100) / 500.0
            else:
                self.angle -= random(100) / 500.0

        self.speed += (-50 + random(100)) / 100.0

        dx = math.sin(self.angle) * 10

        self._mouse_eye_direction = [dx / 5, 0.0][abs(dx / 5) < 1]

        self.setRotation(self.rotation() + dx)
        self.setPos(self.mapToParent(0, -(3 + math.sin(self.speed) * 3)))


if __name__ == '__main__':
    MOUSE_COUNT = 7
    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    scene.setSceneRect(-300, -300, 600, 600)
    scene.setItemIndexMethod(QGraphicsScene.NoIndex)

    for i in range(MOUSE_COUNT):
        mouse = Mouse()
        mouse.setPos(math.sin((i * 6.28) / MOUSE_COUNT) * 200,
                     math.cos((i * 6.28) / MOUSE_COUNT) * 200)
        scene.addItem(mouse)

    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)
    view.setBackgroundBrush(QBrush(QPixmap(':/images/cheese.jpg')))
    view.setCacheMode(QGraphicsView.CacheBackground)
    view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
    view.setDragMode(QGraphicsView.ScrollHandDrag)
    view.setWindowTitle("Colliding Mice")
    view.resize(400, 300)
    view.show()

    timer = QTimer()
    timer.timeout.connect(scene.advance)
    timer.start(1000 / 33)
    sys.exit(app.exec())
