# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import numpy
import sys

from PySide6.QtCore import QRangeModel
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QListView, QMainWindow, QTableView, QTabWidget


STRING_LIST = ["item1", "item2", "item3", "item4"]
INT_LIST = [1, 2, 3]
INT_TABLE = [[1, 2], [3, 4], [5, 6]]
STRING_TABLE = [["item11", "item12"], ["item21", "item22"]]

NP_INT_ARRAY = numpy.array([1, 2, 3], dtype=numpy.int32)
NP_DOUBLE_ARRAY = numpy.array([1.1, 2.2, 3.3], dtype=numpy.double)

NP_INT_TABLE = numpy.array([[1, 2, 3], [4, 5, 6]], dtype=numpy.int32)
NP_DOUBLE_TABLE = numpy.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]], dtype=numpy.double)


def print_numpy_data():
    print("--------------------------------")
    print("NP_INT_ARRAY=", NP_INT_ARRAY)
    print("NP_INT_TABLE=", NP_INT_TABLE)
    print("NP_DOUBLE_ARRAY=", NP_DOUBLE_ARRAY)
    print("NP_DOUBLE_TABLE=", NP_DOUBLE_TABLE)
    print("---------------------------------\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setMinimumWidth(600)
    file_menu = window.menuBar().addMenu("File")
    file_menu.addAction("Output numpy data", print_numpy_data)
    file_menu.addAction("Quit", QKeySequence(QKeySequence.StandardKey.Quit), window.close)
    help_menu = window.menuBar().addMenu("Help")
    help_menu.addAction("About Qt", app.aboutQt)

    tab_widget = QTabWidget()
    window.setCentralWidget(tab_widget)

    list_view = QListView()
    model = QRangeModel(STRING_LIST)
    list_view.setModel(model)
    tab_widget.addTab(list_view, "Python String List")

    list_view = QListView()
    model = QRangeModel(INT_LIST)
    list_view.setModel(model)
    tab_widget.addTab(list_view, "Python int List")

    table_view = QTableView()
    model = QRangeModel(INT_TABLE)
    table_view.setModel(model)
    tab_widget.addTab(table_view, "Python Int Table")

    table_view = QTableView()
    model = QRangeModel(STRING_TABLE)
    table_view.setModel(model)
    tab_widget.addTab(table_view, "Python String Table")

    list_view = QListView()
    model = QRangeModel(NP_INT_ARRAY)
    list_view.setModel(model)
    tab_widget.addTab(list_view, "Numpy Int List")

    list_view = QListView()
    model = QRangeModel(NP_DOUBLE_ARRAY)
    list_view.setModel(model)
    tab_widget.addTab(list_view, "Numpy Double List")

    table_view = QTableView()
    model = QRangeModel(NP_INT_TABLE)
    table_view.setModel(model)
    tab_widget.addTab(table_view, "Numpy Int Table")

    table_view = QTableView()
    model = QRangeModel(NP_DOUBLE_TABLE)
    table_view.setModel(model)
    tab_widget.addTab(table_view, "Numpy Double Table")

    window.setWindowTitle("QRangeModel")
    window.show()
    sys.exit(app.exec())
