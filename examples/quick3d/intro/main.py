# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import os
import sys
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication, QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine

from PySide6.QtQuick3D import QQuick3D

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    QSurfaceFormat.setDefaultFormat(QQuick3D.idealSurfaceFormat(4))

    engine = QQmlApplicationEngine()
    qml_file = os.fspath(Path(__file__).resolve().parent / 'main.qml')
    engine.load(QUrl.fromLocalFile(qml_file))
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
