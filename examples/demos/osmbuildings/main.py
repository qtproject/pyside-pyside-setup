# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import argparse
import sys
from pathlib import Path

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication

from geometry import OSMGeometry  # noqa: F401
from manager import OSMManager, CustomTextureData  # noqa: F401


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSM Buildings")
    parser.add_argument("--disable-buildings", "-b", action="store_true")
    args = parser.parse_args()

    if args.disable_buildings:
        OSMManager.buildings = False

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("OSMBuildings", "Main")
    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = QGuiApplication.exec()
    del engine
    sys.exit(exit_code)
