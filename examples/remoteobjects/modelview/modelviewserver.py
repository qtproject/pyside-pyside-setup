# Copyright (C) 2017 Ford Motor Company
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the remoteobjects/modelviewserver example from Qt v5.x"""

import sys

from PySide6.QtCore import (Qt, QByteArray, QModelIndex, QObject, QTimer, QUrl)
from PySide6.QtGui import (QColor, QStandardItemModel, QStandardItem)
from PySide6.QtWidgets import (QApplication, QTreeView)
from PySide6.QtRemoteObjects import QRemoteObjectHost, QRemoteObjectRegistryHost


class TimerHandler(QObject):
    def __init__(self, model):
        super().__init__()
        self._model = model

    def change_data(self):
        for i in range(10, 50):
            self._model.setData(self._model.index(i, 1),
                                QColor(Qt.blue), Qt.BackgroundRole)

    def insert_data(self):
        self._model.insertRows(2, 9)
        for i in range(2, 11):
            self._model.setData(self._model.index(i, 1),
                                QColor(Qt.green), Qt.BackgroundRole)
            self._model.setData(self._model.index(i, 1),
                                "InsertedRow", Qt.DisplayRole)

    def remove_data(self):
        self._model.removeRows(2, 4)

    def change_flags(self):
        item = self._model.item(0, 0)
        item.setEnabled(False)
        item = item.child(0, 0)
        item.setFlags(item.flags() & Qt.ItemIsSelectable)

    def move_data(self):
        self._model.moveRows(QModelIndex(), 2, 4, QModelIndex(), 10)


def add_child(num_children, nesting_level):
    result = []
    if nesting_level == 0:
        return result
    for i in range(num_children):
        child = QStandardItem(f"Child num {i + 1}, nesting Level {nesting_level}")
        if i == 0:
            child.appendRow(add_child(num_children, nesting_level - 1))
        result.append(child)
    return result


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model_size = 100000
    data_list = []
    source_model = QStandardItemModel()
    horizontal_header_list = ["First Column with spacing",
                              "Second Column with spacing"]
    source_model.setHorizontalHeaderLabels(horizontal_header_list)
    for i in range(model_size):
        first_item = QStandardItem(f"FancyTextNumber {i}")
        if i == 0:
            first_item.appendRow(add_child(2, 2))
        second_item = QStandardItem(f"FancyRow2TextNumber {i}")
        if i % 2 == 0:
            first_item.setBackground(Qt.red)
        row = [first_item, second_item]
        source_model.invisibleRootItem().appendRow(row)
        data_list.append(f"FancyTextNumber {i}")

    # Needed by QMLModelViewClient
    role_names = {
        Qt.DisplayRole: QByteArray(b'_text'),
        Qt.BackgroundRole: QByteArray(b'_color')
    }
    source_model.setItemRoleNames(role_names)

    roles = [Qt.DisplayRole, Qt.BackgroundRole]

    print("Creating registry host")
    node = QRemoteObjectRegistryHost(QUrl("local:registry"))

    node2 = QRemoteObjectHost(QUrl("local:replica"), QUrl("local:registry"))
    node2.enableRemoting(source_model, "RemoteModel", roles)

    view = QTreeView()
    view.setWindowTitle("SourceView")
    view.setModel(source_model)
    view.show()
    handler = TimerHandler(source_model)
    QTimer.singleShot(5000, handler.change_data)
    QTimer.singleShot(10000, handler.insert_data)
    QTimer.singleShot(11000, handler.change_flags)
    QTimer.singleShot(12000, handler.remove_data)
    QTimer.singleShot(13000, handler.move_data)

    sys.exit(app.exec())
