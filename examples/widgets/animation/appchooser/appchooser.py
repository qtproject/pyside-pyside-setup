# Copyright (C) 2010 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import (QPointF, QPropertyAnimation, QRect, QRectF, Qt,
                            Signal)
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                               QGraphicsWidget)
from PySide6.QtStateMachine import QState, QStateMachine

import appchooser_rc


class Pixmap(QGraphicsWidget):
    clicked = Signal()

    def __init__(self, pix, parent=None):
        super().__init__(parent)

        self.orig = QPixmap(pix)
        self.p = QPixmap(pix)

    def paint(self, painter, option, widget):
        painter.drawPixmap(QPointF(), self.p)

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def setGeometry(self, rect):
        super(Pixmap, self).setGeometry(rect)

        if rect.size().width() > self.orig.size().width():
            self.p = self.orig.scaled(rect.size().toSize())
        else:
            self.p = QPixmap(self.orig)


def create_states(objects, selectedRect, parent):
    for obj in objects:
        state = QState(parent)
        state.assignProperty(obj, 'geometry', selectedRect)
        parent.addTransition(obj.clicked, state)


def create_animations(objects, machine):
    for obj in objects:
        animation = QPropertyAnimation(obj, b'geometry', obj)
        machine.addDefaultAnimation(animation)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    p1 = Pixmap(QPixmap(':/digikam.png'))
    p2 = Pixmap(QPixmap(':/akregator.png'))
    p3 = Pixmap(QPixmap(':/accessories-dictionary.png'))
    p4 = Pixmap(QPixmap(':/k3b.png'))

    p1.setGeometry(QRectF(0.0, 0.0, 64.0, 64.0))
    p2.setGeometry(QRectF(236.0, 0.0, 64.0, 64.0))
    p3.setGeometry(QRectF(236.0, 236.0, 64.0, 64.0))
    p4.setGeometry(QRectF(0.0, 236.0, 64.0, 64.0))

    scene = QGraphicsScene(0, 0, 300, 300)
    scene.setBackgroundBrush(Qt.white)
    scene.addItem(p1)
    scene.addItem(p2)
    scene.addItem(p3)
    scene.addItem(p4)

    window = QGraphicsView(scene)
    window.setFrameStyle(0)
    window.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    machine = QStateMachine()
    machine.setGlobalRestorePolicy(QStateMachine.RestoreProperties)

    group = QState(machine)
    selected_rect = QRect(86, 86, 128, 128)

    idle_state = QState(group)
    group.setInitialState(idle_state)

    objects = [p1, p2, p3, p4]
    create_states(objects, selected_rect, group)
    create_animations(objects, machine)

    machine.setInitialState(group)
    machine.start()

    window.resize(300, 300)
    window.show()

    sys.exit(app.exec())
