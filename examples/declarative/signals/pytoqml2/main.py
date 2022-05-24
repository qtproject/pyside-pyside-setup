# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import os
from pathlib import Path
import sys
from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QmlElement


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "examples.signals.pytoqml2"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class RotateValue(QObject):
    valueChanged = Signal(int, arguments=['val'])

    def __init__(self):
        super().__init__()
        self.r = 0

    @Slot()
    def increment(self):
        self.r = self.r + 10
        self.valueChanged.emit(self.r)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = QQuickView()

    rotatevalue = RotateValue()
    timer = QTimer()
    timer.start(2000)
    view.setInitialProperties({"rotatevalue": rotatevalue})

    qml_file = os.fspath(Path(__file__).resolve().parent / 'view.qml')
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Error:
        sys.exit(-1)

    timer.timeout.connect(rotatevalue.increment)

    view.show()
    res = app.exec()
    # Deleting the view before it goes out of scope is required to make
    # sure all child QML instances are destroyed in the correct order.
    del view
    sys.exit(res)
