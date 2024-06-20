# Copyright (C) 2023 The Qt Company Ltd.
# Copyright (C) 2013 Riverbank Computing Limited.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import math

from PySide6.QtGui import (QVector3D, QVector3DList)


class Logo():
    def __init__(self):
        self.m_data = QVector3DList()
        self.m_data.reserve(5000)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        NUM_SECTORS = 100

        for i in range(NUM_SECTORS):
            angle = (i * 2 * math.pi) / NUM_SECTORS
            x5 = 0.30 * math.sin(angle)
            y5 = 0.30 * math.cos(angle)
            x6 = 0.20 * math.sin(angle)
            y6 = 0.20 * math.cos(angle)

            angle = ((i + 1) * 2 * math.pi) / NUM_SECTORS
            x7 = 0.20 * math.sin(angle)
            y7 = 0.20 * math.cos(angle)
            x8 = 0.30 * math.sin(angle)
            y8 = 0.30 * math.cos(angle)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

    def const_data(self):
        return self.m_data.constData()

    def count(self):
        return len(self.m_data) * 3

    def vertex_count(self):
        return self.count() / 6

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        n = QVector3D.normal(QVector3D(x4 - x1, y4 - y1, 0),
                             QVector3D(x2 - x1, y2 - y1, 0))

        self.add(QVector3D(x1, y1, -0.05), n)
        self.add(QVector3D(x4, y4, -0.05), n)
        self.add(QVector3D(x2, y2, -0.05), n)

        self.add(QVector3D(x3, y3, -0.05), n)
        self.add(QVector3D(x2, y2, -0.05), n)
        self.add(QVector3D(x4, y4, -0.05), n)

        n = QVector3D.normal(QVector3D(x1 - x4, y1 - y4, 0),
                             QVector3D(x2 - x4, y2 - y4, 0))

        self.add(QVector3D(x4, y4, 0.05), n)
        self.add(QVector3D(x1, y1, 0.05), n)
        self.add(QVector3D(x2, y2, 0.05), n)

        self.add(QVector3D(x2, y2, 0.05), n)
        self.add(QVector3D(x3, y3, 0.05), n)
        self.add(QVector3D(x4, y4, 0.05), n)

    def extrude(self, x1, y1, x2, y2):
        n = QVector3D.normal(QVector3D(0, 0, -0.1),
                             QVector3D(x2 - x1, y2 - y1, 0))

        self.add(QVector3D(x1, y1, 0.05), n)
        self.add(QVector3D(x1, y1, -0.05), n)
        self.add(QVector3D(x2, y2, 0.05), n)

        self.add(QVector3D(x2, y2, -0.05), n)
        self.add(QVector3D(x2, y2, 0.05), n)
        self.add(QVector3D(x1, y1, -0.05), n)

    def add(self, v, n):
        self.m_data.append(v)
        self.m_data.append(n)
