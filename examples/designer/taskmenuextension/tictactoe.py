# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Qt, QPoint, QRect, QSize, Property, Slot
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget


EMPTY = '-'
CROSS = 'X'
NOUGHT = 'O'
DEFAULT_STATE = "---------"


class TicTacToe(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = DEFAULT_STATE
        self._turn_number = 0

    def minimumSizeHint(self):
        return QSize(200, 200)

    def sizeHint(self):
        return QSize(200, 200)

    def setState(self, new_state):
        self._turn_number = 0
        self._state = DEFAULT_STATE
        for position in range(min(9, len(new_state))):
            mark = new_state[position]
            if mark == CROSS or mark == NOUGHT:
                self._turn_number += 1
                self._change_state_at(position, mark)
            position += 1
        self.update()

    def state(self):
        return self._state

    @Slot()
    def clear_board(self):
        self._state = DEFAULT_STATE
        self._turn_number = 0
        self.update()

    def _change_state_at(self, pos, new_state):
        self._state = (self._state[:pos] + new_state
                       + self._state[pos + 1:])

    def mousePressEvent(self, event):
        if self._turn_number == 9:
            self.clear_board()
            return
        for position in range(9):
            cell = self._cell_rect(position)
            if cell.contains(event.position().toPoint()):
                if self._state[position] == EMPTY:
                    new_state = CROSS if self._turn_number % 2 == 0 else NOUGHT
                    self._change_state_at(position, new_state)
                    self._turn_number += 1
                    self.update()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            painter.setPen(QPen(Qt.darkGreen, 1))
            painter.drawLine(self._cell_width(), 0,
                             self._cell_width(), self.height())
            painter.drawLine(2 * self._cell_width(), 0,
                             2 * self._cell_width(), self.height())
            painter.drawLine(0, self._cell_height(),
                             self.width(), self._cell_height())
            painter.drawLine(0, 2 * self._cell_height(),
                             self.width(), 2 * self._cell_height())

            painter.setPen(QPen(Qt.darkBlue, 2))

            for position in range(9):
                cell = self._cell_rect(position)
                if self._state[position] == CROSS:
                    painter.drawLine(cell.topLeft(), cell.bottomRight())
                    painter.drawLine(cell.topRight(), cell.bottomLeft())
                elif self._state[position] == NOUGHT:
                    painter.drawEllipse(cell)

            painter.setPen(QPen(Qt.yellow, 3))

            for position in range(0, 8, 3):
                if (self._state[position] != EMPTY
                        and self._state[position + 1] == self._state[position]
                        and self._state[position + 2] == self._state[position]):
                    y = self._cell_rect(position).center().y()
                    painter.drawLine(0, y, self.width(), y)
                    self._turn_number = 9

            for position in range(3):
                if (self._state[position] != EMPTY
                        and self._state[position + 3] == self._state[position]
                        and self._state[position + 6] == self._state[position]):
                    x = self._cell_rect(position).center().x()
                    painter.drawLine(x, 0, x, self.height())
                    self._turn_number = 9

            if (self._state[0] != EMPTY and self._state[4] == self._state[0]
                    and self._state[8] == self._state[0]):
                painter.drawLine(0, 0, self.width(), self.height())
                self._turn_number = 9

            if (self._state[2] != EMPTY and self._state[4] == self._state[2]
                    and self._state[6] == self._state[2]):
                painter.drawLine(0, self.height(), self.width(), 0)
                self._turn_number = 9

    def _cell_rect(self, position):
        h_margin = self.width() / 30
        v_margin = self.height() / 30
        row = int(position / 3)
        column = position - 3 * row
        pos = QPoint(column * self._cell_width() + h_margin,
                     row * self._cell_height() + v_margin)
        size = QSize(self._cell_width() - 2 * h_margin,
                     self._cell_height() - 2 * v_margin)
        return QRect(pos, size)

    def _cell_width(self):
        return self.width() / 3

    def _cell_height(self):
        return self.height() / 3

    state = Property(str, state, setState)
