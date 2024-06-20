# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
from pathlib import Path
import sys

from PySide6.QtCore import QUrl, qWarning
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

import rc_window  # noqa: F401

# Append the parent directory of this file so that Python can find and
# import from the "shared" sibling directory.
sys.path.append(os.fspath(Path(__file__).parent.parent))
from shared import shared_rc  # noqa: F401, E402


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    if sys.platform == "win32":
        QQuickStyle.setStyle("Fusion")
    engine = QQmlEngine()

    # Add the qrc root as QML import path so that the "shared" module
    # can be found.
    engine.addImportPath(":/")

    component = QQmlComponent(engine)
    QQuickWindow.setDefaultAlphaBuffer(True)
    component.loadUrl(QUrl("qrc:///window/window.qml"))
    if component.isReady():
        component.create()
    else:
        qWarning(component.errorString())
        app.exit(1)
    app.exec()
