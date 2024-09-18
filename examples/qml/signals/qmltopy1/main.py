# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
from pathlib import Path
import sys
from PySide6.QtCore import QObject, QUrl, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QmlElement


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "examples.signals.qmltopy1"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Console(QObject):
    """Output stuff on the console."""

    @Slot(str)
    @Slot('double')
    def output(self, s):
        print(s)

    @Slot(str)
    def outputStr(self, s):
        print(s)

    @Slot('double')
    def outputFloat(self, x):
        print(x)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = QQuickView()

    qml_file = os.fspath(Path(__file__).resolve().parent / 'view.qml')
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Status.Error:
        sys.exit(-1)
    view.show()
    res = app.exec()
    # Deleting the view before it goes out of scope is required to make sure all child QML instances
    # are destroyed in the correct order.
    del view
    sys.exit(res)
