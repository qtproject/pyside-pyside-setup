# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt DataVisualization graphgallery example from Qt v6.x"""

import os
import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMessageBox, QTabWidget

from bargraph import BarGraph
from scattergraph import ScatterGraph
from surfacegraph import SurfaceGraph


if __name__ == "__main__":
    os.environ["QSG_RHI_BACKEND"] = "opengl"

    app = QApplication(sys.argv)

    # Create a tab widget for creating own tabs for Q3DBars, Q3DScatter, and Q3DSurface
    tabWidget = QTabWidget()
    tabWidget.setWindowTitle("Graph Gallery")

    screen_size = tabWidget.screen().size()
    minimum_graph_size = QSize(screen_size.width() / 2, screen_size.height() / 1.75)

    # Create bar graph
    bars = BarGraph()
    # Create scatter graph
    scatter = ScatterGraph()
    # Create surface graph
    surface = SurfaceGraph()

    if (not bars.initialize(minimum_graph_size, screen_size)
            or not scatter.initialize(minimum_graph_size, screen_size)
            or not surface.initialize(minimum_graph_size, screen_size)):
        QMessageBox.warning(None, "Graph Gallery", "Couldn't initialize the OpenGL context.")
        sys.exit(-1)

    # Add bars widget
    tabWidget.addTab(bars.barsWidget(), "Bar Graph")
    # Add scatter widget
    tabWidget.addTab(scatter.scatterWidget(), "Scatter Graph")
    # Add surface widget
    tabWidget.addTab(surface.surfaceWidget(), "Surface Graph")

    tabWidget.show()
    sys.exit(app.exec())
