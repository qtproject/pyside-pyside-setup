# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface

from window_singlethreaded import WindowSingleThreaded


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    # only functional when Qt Quick is also using OpenGL
    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGLRhi)
    window = WindowSingleThreaded()
    window.resize(1024, 768)
    window.show()
    ex = app.exec()
    del window
    sys.exit(ex)
