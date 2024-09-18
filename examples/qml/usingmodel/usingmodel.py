# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import sys
from PySide6.QtCore import QAbstractListModel, Qt, QUrl, QByteArray
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QmlElement, QmlSingleton


QML_IMPORT_NAME = "PersonModel"
QML_IMPORT_MAJOR_VERSION = 1


@dataclass
class Person:
    name: str
    myrole: str


@QmlElement
@QmlSingleton
class PersonModel (QAbstractListModel):
    MyRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data

    def roleNames(self):
        roles = {
            PersonModel.MyRole: QByteArray(b'myrole'),
            Qt.ItemDataRole.DisplayRole: QByteArray(b'display')
        }
        return roles

    def rowCount(self, index):
        return len(self._data)

    def data(self, index, role):
        d = self._data[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return d.name
        if role == Qt.ItemDataRole.DecorationRole:
            return Qt.black
        if role == PersonModel.MyRole:
            return d.myrole
        return None

    @staticmethod
    def create(engine):
        data = [Person('Qt', 'myrole'), Person('PySide', 'role2')]
        return PersonModel(data)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    qml_file = os.fspath(Path(__file__).resolve().parent / 'view.qml')
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Status.Error:
        sys.exit(-1)
    view.show()

    r = app.exec()
    # Deleting the view before it goes out of scope is required to make sure all child QML instances
    # are destroyed in the correct order.
    del view
    sys.exit(r)
