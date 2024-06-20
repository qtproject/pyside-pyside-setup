# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from gradienttexture import GradientTexture  # noqa: F401

from pathlib import Path

import os
import sys

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("QtProject")
    app.setApplicationName("ProceduralTexture")

    engine = QQmlApplicationEngine()
    app_dir = Path(__file__).parent
    engine.addImportPath(os.fspath(app_dir))
    engine.loadFromModule("ProceduralTextureModule", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    ex = app.exec()
    del engine

    sys.exit(ex)
