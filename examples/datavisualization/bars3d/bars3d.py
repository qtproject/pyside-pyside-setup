# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 QtDataVisualization example"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QSizePolicy, QMainWindow, QWidget
from PySide6.QtDataVisualization import (Q3DBars, QBar3DSeries, QBarDataItem,
                                         QCategory3DAxis, QValue3DAxis)


def data_to_bar_data_row(data):
    return list(QBarDataItem(d) for d in data)


def data_to_bar_data_array(data):
    return list(data_to_bar_data_row(row) for row in data)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Qt DataVisualization 3D Bars')

        self.bars = Q3DBars()

        self._column_axis = QCategory3DAxis()
        self._column_axis.setTitle('Columns')
        self._column_axis.setTitleVisible(True)
        self._column_axis.setLabels(['Column1', 'Column2'])
        self._column_axis.setLabelAutoRotation(30)

        self._row_axis = QCategory3DAxis()
        self._row_axis.setTitle('Rows')
        self._row_axis.setTitleVisible(True)
        self._row_axis.setLabels(['Row1', 'Row2'])
        self._row_axis.setLabelAutoRotation(30)

        self._value_axis = QValue3DAxis()
        self._value_axis.setTitle('Values')
        self._value_axis.setTitleVisible(True)
        self._value_axis.setRange(0, 5)

        self.bars.setRowAxis(self._row_axis)
        self.bars.setColumnAxis(self._column_axis)
        self.bars.setValueAxis(self._value_axis)

        self.series = QBar3DSeries()
        self._array_data = [[1, 2], [3, 4]]
        self.series.dataProxy().addRows(data_to_bar_data_array(self._array_data))

        self.bars.setPrimarySeries(self.series)

        self.container = QWidget.createWindowContainer(self.bars)

        if not self.bars.hasContext():
            print("Couldn't initialize the OpenGL context.")
            sys.exit(-1)

        camera = self.bars.scene().activeCamera()
        camera.setYRotation(22.5)

        geometry = QGuiApplication.primaryScreen().geometry()
        size = geometry.height() * 3 / 4
        self.container.setMinimumSize(size, size)

        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(self.container)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
