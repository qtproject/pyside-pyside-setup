# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""
The gallery example is a simple application with a drawer menu that contains
all the Qt Quick Controls. Each menu item opens a page that shows the
graphical appearance of a control, allows you to interact with the control,
and explains in which circumstances it is handy to use this control.
"""

import os
import sys
import platform

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtCore import QSettings, QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

import rc_gallery  # noqa: F401

if __name__ == "__main__":
    QGuiApplication.setApplicationName("Gallery")
    QGuiApplication.setOrganizationName("QtProject")

    app = QGuiApplication()
    QIcon.setThemeName("gallery")

    settings = QSettings()
    if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        style_name = settings.value("style")
        if style_name:
            QQuickStyle.setStyle(style_name)

    engine = QQmlApplicationEngine()

    built_in_styles = ["Basic", "Fusion", "Imagine", "Material", "Universal"]
    if platform.system() == "Darwin":
        built_in_styles.append("macOS")
    elif platform.system() == "Windows":
        built_in_styles.append("Windows")
    engine.setInitialProperties({"builtInStyles": built_in_styles})

    engine.load(QUrl.fromLocalFile(":/gallery.qml"))
    rootObjects = engine.rootObjects()
    if not rootObjects:
        sys.exit(-1)

    window = rootObjects[0]
    window.setIcon(QIcon(':/qt-project.org/logos/pysidelogo.png'))

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
