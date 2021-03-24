
#############################################################################
##
## Copyright (C) 2016 The Qt Company Ltd.
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

# PySide6 tutorial 14


import sys
import math
import random
from PySide6 import QtCore, QtGui, QtWidgets


class LCDRange(QtWidgets.QWidget):
    value_changed = QtCore.Signal(int)
    def __init__(self, text=None, parent=None):
        if isinstance(text, QtWidgets.QWidget):
            parent = text
            text = None

        QtWidgets.QWidget.__init__(self, parent)

        self.init()

        if text:
            self.set_text(text)

    def init(self):
        lcd = QtWidgets.QLCDNumber(2)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 99)
        self.slider.setValue(0)
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        self.connect(self.slider, QtCore.SIGNAL("valueChanged(int)"),
                     lcd, QtCore.SLOT("display(int)"))
        self.connect(self.slider, QtCore.SIGNAL("valueChanged(int)"),
                     self, QtCore.SIGNAL("valueChanged(int)"))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(lcd)
        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setFocusProxy(self.slider)

    def value(self):
        return self.slider.value()

    @QtCore.Slot(int)
    def set_value(self, value):
        self.slider.setValue(value)

    def text(self):
        return self.label.text()

    def set_range(self, minValue, maxValue):
        if minValue < 0 or maxValue > 99 or minValue > maxValue:
            QtCore.qWarning(f"LCDRange::setRange({minValue}, {maxValue})\n"
                    "\tRange must be 0..99\n"
                    "\tand minValue must not be greater than maxValue")
            return

        self.slider.setRange(minValue, maxValue)

    def set_text(self, text):
        self.label.setText(text)


class CannonField(QtWidgets.QWidget):
    angle_changed = QtCore.Signal(int)
    force_changed = QtCore.Signal(int)
    hit = QtCore.Signal()
    missed = QtCore.Signal()
    can_shoot = QtCore.Signal(bool)
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self._current_angle = 45
        self._current_force = 0
        self._timer_count = 0
        self._auto_shoot_timer = QtCore.QTimer(self)
        self.connect(self._auto_shoot_timer, QtCore.SIGNAL("timeout()"),
                     self.move_shot)
        self._shoot_angle = 0
        self._shoot_force = 0
        self.target = QtCore.QPoint(0, 0)
        self._game_ended = False
        self._barrel_pressed = False
        self.setPalette(QtGui.QPalette(QtGui.QColor(250, 250, 200)))
        self.setAutoFillBackground(True)
        self.new_target()

    def angle(self):
        return self._current_angle

    @QtCore.Slot(int)
    def set_angle(self, angle):
        if angle < 5:
            angle = 5
        if angle > 70:
            angle = 70
        if self._current_angle == angle:
            return
        self._current_angle = angle
        self.update()
        self.emit(QtCore.SIGNAL("angleChanged(int)"), self._current_angle)

    def force(self):
        return self._current_force

    @QtCore.Slot(int)
    def set_force(self, force):
        if force < 0:
            force = 0
        if self._current_force == force:
            return
        self._current_force = force
        self.emit(QtCore.SIGNAL("forceChanged(int)"), self._current_force)

    @QtCore.Slot()
    def shoot(self):
        if self.is_shooting():
            return
        self._timer_count = 0
        self._shoot_angle = self._current_angle
        self._shoot_force = self._current_force
        self._auto_shoot_timer.start(5)
        self.emit(QtCore.SIGNAL("canShoot(bool)"), False)

    first_time = True

    def new_target(self):
        if CannonField.first_time:
            CannonField.first_time = False
            midnight = QtCore.QTime(0, 0, 0)
            random.seed(midnight.secsTo(QtCore.QTime.currentTime()))

        self.target = QtCore.QPoint(200 + random.randint(0, 190 - 1), 10 + random.randint(0, 255 - 1))
        self.update()

    def set_game_over(self):
        if self._game_ended:
            return
        if self.is_shooting():
            self._auto_shoot_timer.stop()
        self._game_ended = True
        self.update()

    def restart_game(self):
        if self.is_shooting():
            self._auto_shoot_timer.stop()
        self._game_ended = False
        self.update()
        self.emit(QtCore.SIGNAL("canShoot(bool)"), True)

    @QtCore.Slot()
    def move_shot(self):
        region = QtGui.QRegion(self.shot_rect())
        self._timer_count += 1

        shot_r = self.shot_rect()

        if shot_r.intersects(self.target_rect()):
            self._auto_shoot_timer.stop()
            self.emit(QtCore.SIGNAL("hit()"))
            self.emit(QtCore.SIGNAL("canShoot(bool)"), True)
        elif shot_r.x() > self.width() or shot_r.y() > self.height() or shot_r.intersects(self.barrier_rect()):
            self._auto_shoot_timer.stop()
            self.emit(QtCore.SIGNAL("missed()"))
            self.emit(QtCore.SIGNAL("canShoot(bool)"), True)
        else:
            region = region.united(QtGui.QRegion(shot_r))

        self.update(region)

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            return
        if self.barrel_hit(event.position().toPoint()):
            self._barrel_pressed = True

    def mouseMoveEvent(self, event):
        if not self._barrel_pressed:
            return
        pos = event.position().toPoint()
        if pos.x() <= 0:
            pos.setX(1)
        if pos.y() >= self.height():
            pos.setY(self.height() - 1)
        rad = math.atan((float(self.rect().bottom()) - pos.y()) / pos.x())
        self.set_angle(round(rad * 180 / 3.14159265))

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._barrel_pressed = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self._game_ended:
            painter.setPen(QtCore.Qt.black)
            painter.setFont(QtGui.QFont("Courier", 48, QtGui.QFont.Bold))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "Game Over")

        self.paint_cannon(painter)
        self.paint_barrier(painter)
        if self.is_shooting():
            self.paint_shot(painter)
        if not self._game_ended:
            self.paint_target(painter)

    def paint_shot(self, painter):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.black)
        painter.drawRect(self.shot_rect())

    def paint_target(self, painter):
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.red)
        painter.drawRect(self.target_rect())

    def paint_barrier(self, painter):
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.yellow)
        painter.drawRect(self.barrier_rect())

    barrel_rect = QtCore.QRect(33, -4, 15, 8)

    def paint_cannon(self, painter):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.blue)

        painter.save()
        painter.translate(0, self.height())
        painter.drawPie(QtCore.QRect(-35, -35, 70, 70), 0, 90 * 16)
        painter.rotate(-self._current_angle)
        painter.drawRect(CannonField.barrel_rect)
        painter.restore()

    def cannon_rect(self):
        result = QtCore.QRect(0, 0, 50, 50)
        result.moveBottomLeft(self.rect().bottomLect())
        return result

    def shot_rect(self):
        gravity = 4.0

        time = self._timer_count / 40.0
        velocity = self._shoot_force
        radians = self._shoot_angle * 3.14159265 / 180

        velx = velocity * math.cos(radians)
        vely = velocity * math.sin(radians)
        x0 = (CannonField.barrel_rect.right() + 5) * math.cos(radians)
        y0 = (CannonField.barrel_rect.right() + 5) * math.sin(radians)
        x = x0 + velx * time
        y = y0 + vely * time - 0.5 * gravity * time * time

        result = QtCore.QRect(0, 0, 6, 6)
        result.moveCenter(QtCore.QPoint(round(x), self.height() - 1 - round(y)))
        return result

    def target_rect(self):
        result = QtCore.QRect(0, 0, 20, 10)
        result.moveCenter(QtCore.QPoint(self.target.x(), self.height() - 1 - self.target.y()))
        return result

    def barrier_rect(self):
        return QtCore.QRect(145, self.height() - 100, 15, 99)

    def barrel_hit(self, pos):
        matrix = QtGui.QTransform()
        matrix.translate(0, self.height())
        matrix.rotate(-self._current_angle)
        matrix, invertible = matrix.inverted()
        return self.barrel_rect.contains(matrix.map(pos))

    def game_over(self):
        return self._game_ended

    def is_shooting(self):
        return self._auto_shoot_timer.isActive()

    def sizeHint(self):
        return QtCore.QSize(400, 300)


class GameBoard(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        quit = QtWidgets.QPushButton("&Quit")
        quit.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))

        self.connect(quit, QtCore.SIGNAL("clicked()"),
                     qApp, QtCore.SLOT("quit()"))

        angle = LCDRange("ANGLE")
        angle.set_range(5, 70)

        force = LCDRange("FORCE")
        force.set_range(10, 50)

        cannon_box = QtWidgets.QFrame()
        cannon_box.setFrameStyle(QtWidgets.QFrame.WinPanel | QtWidgets.QFrame.Sunken)

        self._cannon_field = CannonField()

        self.connect(angle, QtCore.SIGNAL("valueChanged(int)"),
                     self._cannon_field.set_angle)
        self.connect(self._cannon_field, QtCore.SIGNAL("angleChanged(int)"),
                     angle.set_value)

        self.connect(force, QtCore.SIGNAL("valueChanged(int)"),
                     self._cannon_field.set_force)
        self.connect(self._cannon_field, QtCore.SIGNAL("forceChanged(int)"),
                     force.set_value)

        self.connect(self._cannon_field, QtCore.SIGNAL("hit()"), self.hit)
        self.connect(self._cannon_field, QtCore.SIGNAL("missed()"), self.missed)

        shoot = QtWidgets.QPushButton("&Shoot")
        shoot.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))

        self.connect(shoot, QtCore.SIGNAL("clicked()"), self.fire)
        self.connect(self._cannon_field, QtCore.SIGNAL("canShoot(bool)"),
                     shoot, QtCore.SLOT("setEnabled(bool)"))

        restart = QtWidgets.QPushButton("&New Game")
        restart.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))

        self.connect(restart, QtCore.SIGNAL("clicked()"), self.new_game)

        self.hits = QtWidgets.QLCDNumber(2)
        self._shots_left = QtWidgets.QLCDNumber(2)
        hits_label = QtWidgets.QLabel("HITS")
        shots_left_label = QtWidgets.QLabel("SHOTS LEFT")

        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter),
                        self, self.fire)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return),
                        self, self.fire)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Q),
                        self, QtCore.SLOT("close()"))

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(shoot)
        top_layout.addWidget(self.hits)
        top_layout.addWidget(hits_label)
        top_layout.addWidget(self._shots_left)
        top_layout.addWidget(shots_left_label)
        top_layout.addStretch(1)
        top_layout.addWidget(restart)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(angle)
        left_layout.addWidget(force)

        cannon_layout = QtWidgets.QVBoxLayout()
        cannon_layout.addWidget(self._cannon_field)
        cannon_box.setLayout(cannon_layout)

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(quit, 0, 0)
        grid_layout.addLayout(top_layout, 0, 1)
        grid_layout.addLayout(left_layout, 1, 0)
        grid_layout.addWidget(cannon_box, 1, 1, 2, 1)
        grid_layout.setColumnStretch(1, 10)
        self.setLayout(grid_layout)

        angle.set_value(60)
        force.set_value(25)
        angle.setFocus()

        self.new_game()

    @QtCore.Slot()
    def fire(self):
        if self._cannon_field.game_over() or self._cannon_field.is_shooting():
            return
        self._shots_left.display(self._shots_left.intValue() - 1)
        self._cannon_field.shoot()

    @QtCore.Slot()
    def hit(self):
        self.hits.display(self.hits.intValue() + 1)
        if self._shots_left.intValue() == 0:
            self._cannon_field.set_game_over()
        else:
            self._cannon_field.new_target()

    @QtCore.Slot()
    def missed(self):
        if self._shots_left.intValue() == 0:
            self._cannon_field.set_game_over()

    @QtCore.Slot()
    def new_game(self):
        self._shots_left.display(15)
        self.hits.display(0)
        self._cannon_field.restart_game()
        self._cannon_field.new_target()


app = QtWidgets.QApplication(sys.argv)
board = GameBoard()
board.setGeometry(100, 100, 500, 355)
board.show()
sys.exit(app.exec_())
