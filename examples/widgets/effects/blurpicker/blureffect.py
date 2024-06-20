# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations


from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsBlurEffect


class BlurEffect(QGraphicsBlurEffect):
    def __init__(self, item):
        super().__init__()
        self._base_line = 200
        self._item = item

    def adjust_for_item(self):
        y = self._base_line - self._item.pos().y()

        # radius = qBound(qreal(0.0), y / 32, qreal(16.0)); which is equivalent to
        radius = max(0, min(y / 32, 16))

        self.setBlurRadius(radius)

    def set_base_line(self, base_line):
        self._base_line = base_line

    def boundingRect(self) -> QRect:
        self.adjust_for_item()
        return super().boundingRect()

    def draw(self, painter: QPainter):
        self.adjust_for_item()
        super().draw(painter)
