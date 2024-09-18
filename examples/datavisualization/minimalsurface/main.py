# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QVector3D
from PySide6.QtDataVisualization import (Q3DSurface, QSurfaceDataItem,
                                         QSurface3DSeries)


DESCRIPTION = """Minimal Qt DataVisualization Surface Example

Use the mouse wheel to zoom. Rotate using the right mouse button.
"""


if __name__ == '__main__':
    os.environ["QSG_RHI_BACKEND"] = "opengl"
    app = QGuiApplication(sys.argv)

    print(DESCRIPTION)

    surface = Q3DSurface()
    surface.setFlags(surface.flags() ^ Qt.WindowType.FramelessWindowHint)
    axis = surface.axisX()
    axis.setTitle("X")
    axis.setTitleVisible(True)
    axis = surface.axisY()
    axis.setTitle("Y")
    axis.setTitleVisible(True)
    axis = surface.axisZ()
    axis.setTitle("Z")
    axis.setTitleVisible(True)

    data = []
    data_row1 = [QSurfaceDataItem(QVector3D(0, 0.1, 0.5)),
                 QSurfaceDataItem(QVector3D(1, 0.5, 0.5))]
    data.append(data_row1)
    data_row2 = [QSurfaceDataItem(QVector3D(0, 1.8, 1)),
                 QSurfaceDataItem(QVector3D(1, 1.2, 1))]
    data.append(data_row2)

    series = QSurface3DSeries()
    series.dataProxy().resetArray(data)
    surface.addSeries(series)

    available_height = app.primaryScreen().availableGeometry().height()
    width = available_height * 4 / 5
    surface.resize(QSize(width, width))
    surface.show()

    sys.exit(app.exec())
