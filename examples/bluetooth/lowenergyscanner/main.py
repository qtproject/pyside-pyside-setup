# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the bluetooth/lowenergyscanner example from Qt v6.x"""


import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from device import Device  # noqa: F401
from pathlib import Path

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("Scanner", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    ex = QCoreApplication.exec()
    del engine
    sys.exit(ex)
