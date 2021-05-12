
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

import sys
import math

from PySide6.QtCore import (QEasingCurve, QLineF, QMimeData, QPoint, QPointF,
                            QRandomGenerator, QRectF, QTimeLine, Qt)
from PySide6.QtGui import (QBrush, QColor, QDrag, QImage, QPainter, QPixmap,
                           QPen, QTransform)
from PySide6.QtWidgets import (QApplication, QGraphicsItem,
                               QGraphicsItemAnimation, QGraphicsScene,
                               QGraphicsView, QWidget)

import dragdroprobot_rc


def random(boundary):
    return QRandomGenerator.global_().bounded(boundary)


class ColorItem(QGraphicsItem):
    n = 0

    def __init__(self):
        super().__init__()

        self.color = QColor(random(256), random(256), random(256))

        (r, g, b) = (self.color.red(), self.color.green(), self.color.blue())
        self.setToolTip(
            f"QColor({r}, {g}, {b})\nClick and drag this color onto the robot!")
        self.setCursor(Qt.OpenHandCursor)
        self._start_drag_distance = QApplication.startDragDistance()

    def boundingRect(self):
        return QRectF(-15.5, -15.5, 34, 34)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        painter.drawEllipse(-12, -12, 30, 30)
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(-15, -15, 30, 30)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            return

        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        start = QPointF(event.buttonDownScreenPos(Qt.LeftButton))
        if QLineF(event.screenPos(), start).length() < self._start_drag_distance:
            return

        drag = QDrag(event.widget())
        mime = QMimeData()
        drag.setMimeData(mime)

        ColorItem.n += 1
        if ColorItem.n > 2 and random(3) == 0:
            image = QImage(':/images/head.png')
            mime.setImageData(image)
            drag.setPixmap(QPixmap.fromImage(image).scaled(30, 40))
            drag.setHotSpot(QPoint(15, 30))
        else:
            mime.setColorData(self.color)
            (r, g, b) = (self.color.red(), self.color.green(), self.color.blue())
            mime.setText(f"#{r:02x}{g:02x}{b:02x}")

            pixmap = QPixmap(34, 34)
            pixmap.fill(Qt.white)

            painter = QPainter(pixmap)
            painter.translate(15, 15)
            painter.setRenderHint(QPainter.Antialiasing)
            self.paint(painter, None, None)
            painter.end()

            pixmap.setMask(pixmap.createHeuristicMask())

            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(15, 20))

        drag.exec()
        self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)


class RobotPart(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.color = QColor(Qt.lightGray)
        self.pixmap = None
        self._drag_over = False

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if (event.mimeData().hasColor() or
                (isinstance(self, RobotHead) and event.mimeData().hasImage())):
            event.setAccepted(True)
            self._drag_over = True
            self.update()
        else:
            event.setAccepted(False)

    def dragLeaveEvent(self, event):
        self._drag_over = False
        self.update()

    def dropEvent(self, event):
        self._drag_over = False
        if event.mimeData().hasColor():
            self.color = QColor(event.mimeData().colorData())
        elif event.mimeData().hasImage():
            self.pixmap = QPixmap(event.mimeData().imageData())

        self.update()


class RobotHead(RobotPart):
    def boundingRect(self):
        return QRectF(-15, -50, 30, 50)

    def paint(self, painter, option, widget=None):
        if not self.pixmap:
            painter.setBrush(self._drag_over and self.color.lighter(130)
                                            or self.color)
            painter.drawRoundedRect(-10, -30, 20, 30, 25, 25, Qt.RelativeSize)
            painter.setBrush(Qt.white)
            painter.drawEllipse(-7, -3 - 20, 7, 7)
            painter.drawEllipse(0, -3 - 20, 7, 7)
            painter.setBrush(Qt.black)
            painter.drawEllipse(-5, -1 - 20, 2, 2)
            painter.drawEllipse(2, -1 - 20, 2, 2)
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(-6, -2 - 20, 12, 15, 190 * 16, 160 * 16)
        else:
            painter.scale(.2272, .2824)
            painter.drawPixmap(QPointF(-15 * 4.4, -50 * 3.54), self.pixmap)


class RobotTorso(RobotPart):
    def boundingRect(self):
        return QRectF(-30, -20, 60, 60)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self._drag_over and self.color.lighter(130)
                                        or self.color)
        painter.drawRoundedRect(-20, -20, 40, 60, 25, 25, Qt.RelativeSize)
        painter.drawEllipse(-25, -20, 20, 20)
        painter.drawEllipse(5, -20, 20, 20)
        painter.drawEllipse(-20, 22, 20, 20)
        painter.drawEllipse(0, 22, 20, 20)


class RobotLimb(RobotPart):
    def boundingRect(self):
        return QRectF(-5, -5, 40, 10)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self._drag_over and self.color.lighter(130) or self.color)
        painter.drawRoundedRect(self.boundingRect(), 50, 50,
                Qt.RelativeSize)
        painter.drawEllipse(-5, -5, 10, 10)


class Robot(RobotPart):
    def __init__(self):
        super().__init__()

        self.torsoItem         = RobotTorso(self)
        self.headItem          = RobotHead(self.torsoItem)
        self.upperLeftArmItem  = RobotLimb(self.torsoItem)
        self.lowerLeftArmItem  = RobotLimb(self.upperLeftArmItem)
        self._upper_right_arm_item = RobotLimb(self.torsoItem)
        self._lower_right_arm_item = RobotLimb(self._upper_right_arm_item)
        self._upper_right_leg_item = RobotLimb(self.torsoItem)
        self._lower_right_leg_item = RobotLimb(self._upper_right_leg_item)
        self.upperLeftLegItem  = RobotLimb(self.torsoItem)
        self.lowerLeftLegItem  = RobotLimb(self.upperLeftLegItem)

        self.timeline = QTimeLine()
        settings = [
        #             item               position    rotation at
        #                                 x    y    time 0  /  1
            ( self.headItem,              0,  -18,      20,   -20 ),
            ( self.upperLeftArmItem,    -15,  -10,     190,   180 ),
            ( self.lowerLeftArmItem,     30,    0,      50,    10 ),
            ( self._upper_right_arm_item,    15,  -10,     300,   310 ),
            ( self._lower_right_arm_item,    30,    0,       0,   -70 ),
            ( self._upper_right_leg_item,    10,   32,      40,   120 ),
            ( self._lower_right_leg_item,    30,    0,      10,    50 ),
            ( self.upperLeftLegItem,    -10,   32,     150,    80 ),
            ( self.lowerLeftLegItem,     30,    0,      70,    10 ),
            ( self.torsoItem,             0,    0,       5,   -20 )
        ]
        self.animations = []
        for item, pos_x, pos_y, rotation1, rotation2 in settings:
            item.setPos(pos_x,pos_y)
            animation = QGraphicsItemAnimation()
            animation.setItem(item)
            animation.setTimeLine(self.timeline)
            animation.setRotationAt(0, rotation1)
            animation.setRotationAt(1, rotation2)
            self.animations.append(animation)
        self.animations[0].setScaleAt(1, 1.1, 1.1)

        self.timeline.setUpdateInterval(1000 / 25)
        curve = QEasingCurve(QEasingCurve.SineCurve)
        self.timeline.setEasingCurve(curve)
        self.timeline.setLoopCount(0)
        self.timeline.setDuration(2000)
        self.timeline.start()

    def boundingRect(self):
        return QRectF()

    def paint(self, painter, option, widget=None):
        pass


if __name__== '__main__':
    app = QApplication(sys.argv)

    scene = QGraphicsScene(-200, -200, 400, 400)

    for i in range(10):
        item = ColorItem()
        angle = i * 2.0 * math.pi / 10.0
        item.setPos(math.sin(angle) * 150, math.cos(angle) * 150)
        scene.addItem(item)

    robot = Robot()
    robot.setTransform(QTransform().scale(1.2, 1.2))
    robot.setPos(0, -20)
    scene.addItem(robot)

    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)
    view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
    view.setBackgroundBrush(QColor(230, 200, 167))
    view.setWindowTitle("Drag and Drop Robot")
    view.show()

    sys.exit(app.exec())
