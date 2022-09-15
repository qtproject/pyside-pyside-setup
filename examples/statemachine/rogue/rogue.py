# Copyright (C) 2010 velociraptor Genjix <aphidia@hotmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import (QEvent, QPoint, QRandomGenerator, QSize, Qt,
                            Property)
from PySide6.QtGui import QFont, QFontMetrics, QFontDatabase, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtStateMachine import (QEventTransition, QFinalState,
                                    QKeyEventTransition, QState, QStateMachine)


class MovementTransition(QEventTransition):
    def __init__(self, window):
        super().__init__(window, QEvent.KeyPress)
        self.window = window

    def eventTest(self, event):
        if (event.type() == QEvent.StateMachineWrapped and
                event.event().type() == QEvent.KeyPress):
            key = event.event().key()
            return (key == Qt.Key_2 or key == Qt.Key_8 or
                    key == Qt.Key_6 or key == Qt.Key_4)
        return False

    def onTransition(self, event):
        key = event.event().key()
        if key == Qt.Key_4:
            self.window.move_player(self.window.left)
        if key == Qt.Key_8:
            self.window.move_player(self.window.Up)
        if key == Qt.Key_6:
            self.window.move_player(self.window.right)
        if key == Qt.Key_2:
            self.window.move_player(self.window.down)


class Custom(QState):
    def __init__(self, parent, mw):
        super().__init__(parent)
        self.mw = mw

    def onEntry(self, e):
        print(self.mw.status)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pX = 5
        self.pY = 5
        self.width = 35
        self.height = 20
        self._status_str = ''

        font = QFont()
        if 'Monospace' in QFontDatabase.families():
            font = QFont('Monospace', 12)
        else:
            for family in QFontDatabase.families():
                if QFontDatabase.isFixedPitch(family):
                    font = QFont(family, 12)
        self.setFont(font)

        self.setup_map()
        self.build_machine()
        self.show()

    def setup_map(self):
        self.map = []
        generator = QRandomGenerator().global_()
        for x in range(self.width):
            column = []
            for y in range(self.height):
                if (x == 0 or x == self.width - 1 or y == 0 or
                        y == self.height - 1 or generator.bounded(0, 40) == 0):
                    column.append('#')
                else:
                    column.append('.')
            self.map.append(column)

    def build_machine(self):
        machine = QStateMachine(self)

        input_state = Custom(machine, self)
        # this line sets the status
        self.status = 'hello!'
        # however this line does not
        input_state.assignProperty(self, 'status', 'Move the rogue with 2, 4, 6, and 8')

        machine.setInitialState(input_state)
        machine.start()

        transition = MovementTransition(self)
        input_state.addTransition(transition)

        quit_state = QState(machine)
        quit_state.assignProperty(self, 'status', 'Really quit(y/n)?')

        yes_transition = QKeyEventTransition(self, QEvent.KeyPress, Qt.Key_Y)
        self._final_state = QFinalState(machine)
        yes_transition.setTargetState(self._final_state)
        quit_state.addTransition(yes_transition)

        no_transition = QKeyEventTransition(self, QEvent.KeyPress, Qt.Key_N)
        no_transition.setTargetState(input_state)
        quit_state.addTransition(no_transition)

        quit_transition = QKeyEventTransition(self, QEvent.KeyPress, Qt.Key_Q)
        quit_transition.setTargetState(quit_state)
        input_state.addTransition(quit_transition)

        machine.setInitialState(input_state)
        machine.finished.connect(qApp.quit)
        machine.start()

    def sizeHint(self):
        metrics = QFontMetrics(self.font())
        return QSize(metrics.horizontalAdvance('X') * self.width,
                     metrics.height() * (self.height + 1))

    def paintEvent(self, event):
        metrics = QFontMetrics(self.font())
        with QPainter(self) as painter:
            font_height = metrics.height()
            font_width = metrics.horizontalAdvance('X')

            painter.fillRect(self.rect(), Qt.black)
            painter.setPen(Qt.white)

            y_pos = font_height
            painter.drawText(QPoint(0, y_pos), self.status)
            for y in range(self.height):
                y_pos += font_height
                x_pos = 0
                for x in range(self.width):
                    if y == self.pY and x == self.pX:
                        x_pos += font_width
                        continue
                    painter.drawText(QPoint(x_pos, y_pos), self.map[x][y])
                    x_pos += font_width
            painter.drawText(QPoint(self.pX * font_width, (self.pY + 2) * font_height), '@')

    def move_player(self, direction):
        if direction == self.left:
            if self.map[self.pX - 1][self.pY] != '#':
                self.pX -= 1
        elif direction == self.right:
            if self.map[self.pX + 1][self.pY] != '#':
                self.pX += 1
        elif direction == self.Up:
            if self.map[self.pX][self.pY - 1] != '#':
                self.pY -= 1
        elif direction == self.down:
            if self.map[self.pX][self.pY + 1] != '#':
                self.pY += 1
        self.repaint()

    def get_status(self):
        return self._status_str

    def set_status(self, status):
        self._status_str = status
        self.repaint()
    status = Property(str, get_status, set_status)
    Up = 0
    down = 1
    left = 2
    right = 3
    width = 35
    height = 20


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    sys.exit(app.exec())
