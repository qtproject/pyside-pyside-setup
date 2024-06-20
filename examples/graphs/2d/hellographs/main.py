# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Qt Hello Graphs example from Qt v6.x"""

from pathlib import Path
import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    viewer = QQuickView()
    viewer.engine().addImportPath(Path(__file__).parent)
    viewer.setColor("black")
    viewer.loadFromModule("HelloGraphs", "Main")
    viewer.show()
    r = app.exec()
    del viewer
    sys.exit(r)
