# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView, QQuickWindow, QSGRendererInterface

from squircle import Squircle

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGL)

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    qml_file = Path(__file__).parent / "main.qml"
    view.setSource(QUrl.fromLocalFile(qml_file))

    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()

    sys.exit(app.exec())
