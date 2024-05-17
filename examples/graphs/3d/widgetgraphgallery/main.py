# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt Graphs widgetgallery example from Qt v6.x"""

import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QTabWidget

from bargraph import BarGraph
from scattergraph import ScatterGraph
from surfacegraph import SurfaceGraph


class MainWidget(QTabWidget):
    """Tab widget for creating own tabs for Q3DBars, Q3DScatter, and Q3DSurface"""

    def __init__(self, p=None):
        super().__init__(p)

        screen_size = self.screen().size()
        minimum_graph_size = QSize(screen_size.width() / 2, screen_size.height() / 1.75)

        # Create bar graph
        self._bars = BarGraph(minimum_graph_size, screen_size)
        # Create scatter graph
        self._scatter = ScatterGraph(minimum_graph_size, screen_size)
        # Create surface graph
        self._surface = SurfaceGraph(minimum_graph_size, screen_size)

        # Add bars widget
        self.addTab(self._bars.barsWidget(), "Bar Graph")
        # Add scatter widget
        self.addTab(self._scatter.scatterWidget(), "Scatter Graph")
        # Add surface widget
        self.addTab(self._surface.surfaceWidget(), "Surface Graph")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    tabWidget = MainWidget()
    tabWidget.setWindowTitle("Widget Gallery")

    tabWidget.show()
    exit_code = app.exec()
    del tabWidget
    sys.exit(exit_code)
