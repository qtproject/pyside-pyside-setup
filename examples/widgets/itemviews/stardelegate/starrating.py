# Copyright (C) 2010 Hans-Peter Jansen <hpj@urpla.net>
# Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from math import (cos, sin, pi)

from PySide6.QtGui import (QPainter, QPolygonF)
from PySide6.QtCore import (QPointF, QSize, Qt)

PAINTING_SCALE_FACTOR = 20


class StarRating(object):
    """ Handle the actual painting of the stars themselves. """

    def __init__(self, starCount=1, maxStarCount=5):
        self.star_count = starCount
        self.MAX_STAR_COUNT = maxStarCount

        # Create the star shape we'll be drawing.
        self._star_polygon = QPolygonF()
        self._star_polygon.append(QPointF(1.0, 0.5))
        for i in range(1, 5):
            self._star_polygon.append(QPointF(0.5 + 0.5 * cos(0.8 * i * pi),
                                    0.5 + 0.5 * sin(0.8 * i * pi)))

        # Create the diamond shape we'll show in the editor
        self._diamond_polygon = QPolygonF()
        diamond_points = [QPointF(0.4, 0.5), QPointF(0.5, 0.4),
                         QPointF(0.6, 0.5), QPointF(0.5, 0.6),
                         QPointF(0.4, 0.5)]
        self._diamond_polygon.append(diamond_points)

    def sizeHint(self):
        """ Tell the caller how big we are. """
        return PAINTING_SCALE_FACTOR * QSize(self.MAX_STAR_COUNT, 1)

    def paint(self, painter, rect, palette, isEditable=False):
        """ Paint the stars (and/or diamonds if we're in editing mode). """
        painter.save()

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        if isEditable:
            painter.setBrush(palette.highlight())
        else:
            painter.setBrush(palette.windowText())

        y_offset = (rect.height() - PAINTING_SCALE_FACTOR) / 2
        painter.translate(rect.x(), rect.y() + y_offset)
        painter.scale(PAINTING_SCALE_FACTOR, PAINTING_SCALE_FACTOR)

        for i in range(self.MAX_STAR_COUNT):
            if i < self.star_count:
                painter.drawPolygon(self._star_polygon, Qt.WindingFill)
            elif isEditable:
                painter.drawPolygon(self._diamond_polygon, Qt.WindingFill)
            painter.translate(1.0, 0.0)

        painter.restore()
