# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtCore import Qt

import rc_markers  # noqa: F401


def rectangle(point_type, image_size):
    image = QImage(image_size, image_size, QImage.Format_RGB32)
    painter = QPainter()
    painter.begin(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.fillRect(0, 0, image_size, image_size, point_type[2])
    painter.end()
    return image


def triangle(point_type, image_size):
    return QImage(point_type[3]).scaled(image_size, image_size)


def circle(point_type, image_size):
    image = QImage(image_size, image_size, QImage.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter()
    painter.begin(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(point_type[2])
    pen = painter.pen()
    pen.setWidth(0)
    painter.setPen(pen)
    painter.drawEllipse(0, 0, image_size * 0.9, image_size * 0.9)
    painter.end()
    return image


_point_types = [("RedRectangle", rectangle, Qt.red),
                ("GreenTriangle", triangle, Qt.green, ":/images/green_triangle.png"),
                ("OrangeCircle", circle, QColor(255, 127, 80))]
_selected_point_types = [("BlueTriangle", triangle, Qt.blue, ":/images/blue_triangle.png"),
                         ("YellowRectangle", rectangle, Qt.yellow),
                         ("LavenderCircle", circle, QColor(147, 112, 219))]
_line_colors = [("Blue", QColor(65, 105, 225)), ("Black", Qt.black), ("Mint", QColor(70, 203, 155))]


def point_type(index):
    return _point_types[index]


def selected_point_type(index):
    return _selected_point_types[index]


def line_color(index):
    return _line_colors[index]


def default_light_marker(image_size):
    return rectangle(_point_types[0], image_size)


def default_selected_light_marker(image_size):
    return triangle(_selected_point_types[0], image_size)


def get_point_representation(point_type, image_size):
    return point_type[1](point_type, image_size)


def get_selected_point_representation(point_type, image_size):
    return point_type[1](point_type, image_size)


def make_line_color(line_color):
    return line_color[1]
