# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the examples/statemachine/moveblocks example from Qt v6.x"""

import sys

from PySide6.QtCore import (QAbstractAnimation, QEasingCurve, QEvent, QObject,
                            QParallelAnimationGroup, QPropertyAnimation,
                            QRandomGenerator, QRect, QSequentialAnimationGroup,
                            Qt, QTimer)
from PySide6.QtGui import QPainter, QResizeEvent
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                               QGraphicsWidget, QStyleOptionGraphicsItem,
                               QWidget)
from PySide6.QtStateMachine import (QAbstractTransition, QState, QStateMachine)


StateSwitchType = QEvent.Type(QEvent.Type.User + 256)


class StateSwitchEvent(QEvent):
    def __init__(self, rand: int = 0) -> None:
        super().__init__(StateSwitchType)
        self._rand = rand

    def rand(self) -> int:
        return self._rand


class QGraphicsRectWidget(QGraphicsWidget):
    def __init__(self):
        super().__init__()

    def paint(self, painter: QPainter,
              option: QStyleOptionGraphicsItem, widget: QWidget | None = None):
        painter.fillRect(self.rect(), Qt.blue)


class StateSwitchTransition(QAbstractTransition):
    def __init__(self, rand: int = 0) -> None:
        super().__init__()
        self._rand = rand

    def eventTest(self, event: QEvent) -> bool:
        return event.type() == StateSwitchType and event.rand() == self._rand

    def onTransition(self, event: QEvent):
        pass


class StateSwitcher(QState):
    def __init__(self, machine: QStateMachine) -> None:
        super().__init__(machine)
        self._state_count = 0
        self._last_index = 0
        self.rg = QRandomGenerator.global_()

    def onEntry(self, event: QEvent) -> None:
        while True:
            n = int(self.rg.bounded(self._state_count)) + 1
            if n != self._last_index:
                break
        self._last_index = n
        self.event = StateSwitchEvent(n)
        self.machine().postEvent(self.event)

    def onExit(self, event: QEvent) -> None:
        pass

    def addState(self, state: QState, animation: QAbstractAnimation) -> None:
        self._state_count += 1
        trans = StateSwitchTransition(self._state_count)
        trans.setTargetState(state)
        self.addTransition(trans)
        trans.addAnimation(animation)


def createGeometryState(w1: QObject, rect1: QRect,
                        w2: QObject, rect2: QRect,
                        w3: QObject, rect3: QRect,
                        w4: QObject, rect4: QRect, parent: QState) -> QState:
    result = QState(parent)
    result.assignProperty(w1, "geometry", rect1)
    result.assignProperty(w2, "geometry", rect2)
    result.assignProperty(w3, "geometry", rect3)
    result.assignProperty(w4, "geometry", rect4)

    return result


class GraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent: QWidget | None = None):
        super().__init__(scene, parent)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.fitInView(self.sceneRect())
        super().resizeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    button1, button2 = QGraphicsRectWidget(), QGraphicsRectWidget()
    button3, button4 = QGraphicsRectWidget(), QGraphicsRectWidget()

    button2.setZValue(1)
    button3.setZValue(2)
    button4.setZValue(3)

    scene = QGraphicsScene(0, 0, 300, 300)
    scene.setBackgroundBrush(Qt.black)
    scene.addItem(button1)
    scene.addItem(button2)
    scene.addItem(button3)
    scene.addItem(button4)

    window = GraphicsView(scene)
    window.setFrameStyle(0)
    window.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    machine = QStateMachine()

    group = QState()
    group.setObjectName("group")
    timer = QTimer()
    timer.setInterval(1250)
    timer.setSingleShot(True)

    group.entered.connect(timer.start)

    state1, state2, state3 = QState(), QState(), QState()
    state4, state5, state6 = QState(), QState(), QState()
    state7 = QState()

    state1 = createGeometryState(button1, QRect(100, 0, 50, 50),
                                 button2, QRect(150, 0, 50, 50),
                                 button3, QRect(200, 0, 50, 50),
                                 button4, QRect(250, 0, 50, 50),
                                 group)
    state2 = createGeometryState(button1, QRect(250, 100, 50, 50),
                                 button2, QRect(250, 150, 50, 50),
                                 button3, QRect(250, 200, 50, 50),
                                 button4, QRect(250, 250, 50, 50),
                                 group)
    state3 = createGeometryState(button1, QRect(150, 250, 50, 50),
                                 button2, QRect(100, 250, 50, 50),
                                 button3, QRect(50, 250, 50, 50),
                                 button4, QRect(0, 250, 50, 50),
                                 group)
    state4 = createGeometryState(button1, QRect(0, 150, 50, 50),
                                 button2, QRect(0, 100, 50, 50),
                                 button3, QRect(0, 50, 50, 50),
                                 button4, QRect(0, 0, 50, 50),
                                 group)
    state5 = createGeometryState(button1, QRect(100, 100, 50, 50),
                                 button2, QRect(150, 100, 50, 50),
                                 button3, QRect(100, 150, 50, 50),
                                 button4, QRect(150, 150, 50, 50),
                                 group)
    state6 = createGeometryState(button1, QRect(50, 50, 50, 50),
                                 button2, QRect(200, 50, 50, 50),
                                 button3, QRect(50, 200, 50, 50),
                                 button4, QRect(200, 200, 50, 50),
                                 group)
    state7 = createGeometryState(button1, QRect(0, 0, 50, 50),
                                 button2, QRect(250, 0, 50, 50),
                                 button3, QRect(0, 250, 50, 50),
                                 button4, QRect(250, 250, 50, 50),
                                 group)
    group.setInitialState(state1)

    animation_group = QParallelAnimationGroup()
    sub_group = QSequentialAnimationGroup()

    anim = QPropertyAnimation(button4, b"geometry")
    anim.setDuration(1000)
    anim.setEasingCurve(QEasingCurve.OutElastic)
    animation_group.addAnimation(anim)

    sub_group = QSequentialAnimationGroup(animation_group)
    sub_group.addPause(100)
    anim = QPropertyAnimation(button3, b"geometry")
    anim.setDuration(1000)
    anim.setEasingCurve(QEasingCurve.OutElastic)
    sub_group.addAnimation(anim)

    sub_group = QSequentialAnimationGroup(animation_group)
    sub_group.addPause(150)
    anim = QPropertyAnimation(button2, b"geometry")
    anim.setDuration(1000)
    anim.setEasingCurve(QEasingCurve.OutElastic)
    sub_group.addAnimation(anim)

    sub_group = QSequentialAnimationGroup(animation_group)
    sub_group.addPause(200)
    anim = QPropertyAnimation(button1, b"geometry")
    anim.setDuration(1000)
    anim.setEasingCurve(QEasingCurve.OutElastic)
    sub_group.addAnimation(anim)

    state_switcher = StateSwitcher(machine)
    state_switcher.setObjectName("state_switcher")
    group.addTransition(timer.timeout, state_switcher)
    state_switcher.addState(state1, animation_group)
    state_switcher.addState(state2, animation_group)
    state_switcher.addState(state3, animation_group)
    state_switcher.addState(state4, animation_group)
    state_switcher.addState(state5, animation_group)
    state_switcher.addState(state6, animation_group)
    state_switcher.addState(state7, animation_group)

    machine.addState(group)
    machine.setInitialState(group)
    machine.start()

    window.resize(300, 300)
    window.show()

    sys.exit(app.exec())
