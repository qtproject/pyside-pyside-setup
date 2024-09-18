# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt DataVisualization qmlsurfacegallery example from Qt v6.x"""

import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtDataVisualization import qDefaultSurfaceFormat

from datasource import DataSource  # noqa: F401
import rc_qmlsurfacegallery  # noqa: F401


if __name__ == "__main__":
    os.environ["QSG_RHI_BACKEND"] = "opengl"
    app = QGuiApplication(sys.argv)

    viewer = QQuickView()

    # Enable antialiasing in direct rendering mode
    viewer.setFormat(qDefaultSurfaceFormat(True))

    viewer.engine().quit.connect(QCoreApplication.quit)

    viewer.setTitle("Surface Graph Gallery")

    qml_file = Path(__file__).resolve().parent / "qml" / "qmlsurfacegallery" / "main.qml"
    viewer.setSource(QUrl.fromLocalFile(qml_file))
    viewer.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
    viewer.show()

    ex = app.exec()
    del viewer
    sys.exit(ex)
