# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from textwrap import dedent

from PySide6.QtCore import QSize, Qt, Slot, Signal
from PySide6.QtGui import (QBrush, QFont, QFontDatabase, QFontMetrics,
                           QPainter, QPen)
from PySide6.QtWidgets import QToolTip, QWidget

COLUMNS = 16


class CharacterWidget(QWidget):

    character_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._display_font = QFont()
        self._last_key = -1
        self._square_size = int(0)

        self.calculate_square_size()
        self.setMouseTracking(True)

    @Slot(QFont)
    def update_font(self, font):
        self._display_font.setFamily(font.family())
        self.calculate_square_size()
        self.adjustSize()
        self.update()

    @Slot(str)
    def update_size(self, fontSize):
        self._display_font.setPointSize(int(fontSize))
        self.calculate_square_size()
        self.adjustSize()
        self.update()

    @Slot(str)
    def update_style(self, fontStyle):
        old_strategy = self._display_font.styleStrategy()
        self._display_font = QFontDatabase.font(self._display_font.family(),
                                                fontStyle,
                                                self._display_font.pointSize())
        self._display_font.setStyleStrategy(old_strategy)
        self.calculate_square_size()
        self.adjustSize()
        self.update()

    @Slot(bool)
    def update_font_merging(self, enable):
        if enable:
            self._display_font.setStyleStrategy(QFont.PreferDefault)
        else:
            self._display_font.setStyleStrategy(QFont.NoFontMerging)
        self.adjustSize()
        self.update()

    def calculate_square_size(self):
        h = QFontMetrics(self._display_font, self).height()
        self._square_size = max(16, 4 + h)

    def sizeHint(self):
        return QSize(COLUMNS * self._square_size,
                     (65536 / COLUMNS) * self._square_size)

    def _unicode_from_pos(self, point):
        row = int(point.y() / self._square_size)
        return row * COLUMNS + int(point.x() / self._square_size)

    def mouseMoveEvent(self, event):
        widget_position = self.mapFromGlobal(event.globalPosition().toPoint())
        key = self._unicode_from_pos(widget_position)
        c = chr(key)
        family = self._display_font.family()
        text = dedent(f'''
                       <p>Character: <span style="font-size: 24pt; font-family: {family}">
                       {c}</span><p>Value: 0x{key:x}
                       ''')
        QToolTip.showText(event.globalPosition().toPoint(), text, self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._last_key = self._unicode_from_pos(event.position().toPoint())
            if self._last_key != -1:
                c = chr(self._last_key)
                self.character_selected.emit(f"{c}")
            self.update()
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event):
        with QPainter(self) as painter:
            self.render(event, painter)

    def render(self, event, painter):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QBrush(Qt.white))
        painter.setFont(self._display_font)
        redraw_rect = event.rect()
        begin_row = int(redraw_rect.top() / self._square_size)
        end_row = int(redraw_rect.bottom() / self._square_size)
        begin_column = int(redraw_rect.left() / self._square_size)
        end_column = int(redraw_rect.right() / self._square_size)
        painter.setPen(QPen(Qt.gray))
        for row in range(begin_row, end_row + 1):
            for column in range(begin_column, end_column + 1):
                x = int(column * self._square_size)
                y = int(row * self._square_size)
                painter.drawRect(x, y, self._square_size, self._square_size)

        font_metrics = QFontMetrics(self._display_font)
        painter.setPen(QPen(Qt.black))
        for row in range(begin_row, end_row + 1):
            for column in range(begin_column, end_column + 1):
                key = int(row * COLUMNS + column)
                painter.setClipRect(column * self._square_size,
                                    row * self._square_size,
                                    self._square_size, self._square_size)

                if key == self._last_key:
                    painter.fillRect(column * self._square_size + 1,
                                     row * self._square_size + 1,
                                     self._square_size, self._square_size, QBrush(Qt.red))

                text = chr(key)
                painter.drawText(column * self._square_size + (self._square_size / 2) -
                                 font_metrics.horizontalAdvance(text) / 2,
                                 row * self._square_size + 4 + font_metrics.ascent(),
                                 text)
