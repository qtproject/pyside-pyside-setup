# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import os
from pathlib import Path
import sys
from PySide6.QtCore import QAbstractListModel, Qt, QUrl, QByteArray
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import qmlRegisterSingletonType


class PersonModel (QAbstractListModel):
    MyRole = Qt.UserRole + 1

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._data = []

    def roleNames(self):
        roles = {
            PersonModel.MyRole: QByteArray(b'modelData'),
            Qt.DisplayRole: QByteArray(b'display')
        }
        return roles

    def rowCount(self, index):
        return len(self._data)

    def data(self, index, role):
        d = self._data[index.row()]

        if role == Qt.DisplayRole:
            return d['name']
        elif role == Qt.DecorationRole:
            return Qt.black
        elif role == PersonModel.MyRole:
            return d['myrole']
        return None

    def populate(self, data=None):
        for item in data:
            self._data.append(item)


def model_callback(engine):
    my_model = PersonModel()
    data = [{'name': 'Qt', 'myrole': 'role1'},
            {'name': 'PySide', 'myrole': 'role2'}]
    my_model.populate(data)
    return my_model


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    qmlRegisterSingletonType(PersonModel, "PersonModel", 1, 0, "MyModel", model_callback)
    qml_file = os.fspath(Path(__file__).resolve().parent / 'view.qml')
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()

    r = app.exec()
    # Deleting the view before it goes out of scope is required to make sure all child QML instances
    # are destroyed in the correct order.
    del view
    sys.exit(r)
