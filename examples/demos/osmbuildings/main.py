# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from pathlib import Path

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QCoreApplication

from manager import OSMManager, CustomTextureData  # noqa: F401


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("OSMBuildings", "Main")
    if not engine.rootObjects():
        sys.exit(-1)
    ex = QCoreApplication.exec()
    del engine
    sys.exit(ex)
