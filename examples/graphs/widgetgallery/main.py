# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the Qt Graphs widgetgallery example from Qt v6.x"""

import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QTabWidget

from bargraph import BarGraph
from scattergraph import ScatterGraph
from surfacegraph import SurfaceGraph


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create a tab widget for creating own tabs for Q3DBars, Q3DScatter, and Q3DSurface
    tabWidget = QTabWidget()
    tabWidget.setWindowTitle("Widget Gallery")

    screen_size = tabWidget.screen().size()
    minimum_graph_size = QSize(screen_size.width() / 2, screen_size.height() / 1.75)

    # Create bar graph
    bars = BarGraph(minimum_graph_size, screen_size)
    # Create scatter graph
    scatter = ScatterGraph(minimum_graph_size, screen_size)
    # Create surface graph
    surface = SurfaceGraph(minimum_graph_size, screen_size)

    # Add bars widget
    tabWidget.addTab(bars.barsWidget(), "Bar Graph")
    # Add scatter widget
    tabWidget.addTab(scatter.scatterWidget(), "Scatter Graph")
    # Add surface widget
    tabWidget.addTab(surface.surfaceWidget(), "Surface Graph")

    tabWidget.show()
    sys.exit(app.exec())
