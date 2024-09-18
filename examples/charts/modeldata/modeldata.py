# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Model Data example from Qt v5.x"""

import sys
from random import randrange

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QRect, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView,
                               QTableView, QWidget)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QVXYModelMapper


class CustomTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.input_data = []
        self.mapping = {}
        self.column_count = 4
        self.row_count = 15

        for i in range(self.row_count):
            data_vec = [0] * self.column_count
            for k in range(len(data_vec)):
                if k % 2 == 0:
                    data_vec[k] = i * 50 + randrange(30)
                else:
                    data_vec[k] = randrange(100)
            self.input_data.append(data_vec)

    def rowCount(self, parent=QModelIndex()):
        return len(self.input_data)

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if section % 2 == 0:
                return "x"
            else:
                return "y"
        else:
            return str(section + 1)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.input_data[index.row()][index.column()]
        elif role == Qt.ItemDataRole.EditRole:
            return self.input_data[index.row()][index.column()]
        elif role == Qt.ItemDataRole.BackgroundRole:
            for color, rect in self.mapping.items():
                if rect.contains(index.column(), index.row()):
                    return QColor(color)
            # cell not mapped return white color
            return QColor(Qt.white)
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            self.input_data[index.row()][index.column()] = float(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable

    def add_mapping(self, color, area):
        self.mapping[color] = area

    def clear_mapping(self):
        self.mapping = {}


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.model = CustomTableModel()

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)

        self.series = QLineSeries()
        self.series.setName("Line 1")
        self.mapper = QVXYModelMapper(self)
        self.mapper.setXColumn(0)
        self.mapper.setYColumn(1)
        self.mapper.setSeries(self.series)
        self.mapper.setModel(self.model)
        self.chart.addSeries(self.series)

        # get the color of the series and use it for showing the mapped area
        self.model.add_mapping(self.series.pen().color().name(),
                               QRect(0, 0, 2, self.model.rowCount()))

        # series 2
        self.series = QLineSeries()
        self.series.setName("Line 2")

        self.mapper = QVXYModelMapper(self)
        self.mapper.setXColumn(2)
        self.mapper.setYColumn(3)
        self.mapper.setSeries(self.series)
        self.mapper.setModel(self.model)
        self.chart.addSeries(self.series)

        # get the color of the series and use it for showing the mapped area
        self.model.add_mapping(self.series.pen().color().name(),
                               QRect(2, 0, 2, self.model.rowCount()))

        self.chart.createDefaultAxes()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setMinimumSize(640, 480)

        # create main layout
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.table_view, 1, 0)
        self.main_layout.addWidget(self.chart_view, 1, 1)
        self.main_layout.setColumnStretch(1, 1)
        self.main_layout.setColumnStretch(0, 0)
        self.setLayout(self.main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TableWidget()
    w.show()
    sys.exit(app.exec())
