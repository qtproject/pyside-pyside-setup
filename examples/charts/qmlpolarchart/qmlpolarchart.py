# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the QML Polar Chart Example from Qt v5.x"""

import os
from pathlib import Path
import sys

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = QQuickView()

    src_dir = Path(__file__).resolve().parent
    viewer.engine().addImportPath(os.fspath(src_dir))
    viewer.engine().quit.connect(viewer.close)

    viewer.setTitle = "QML Polar Chart"
    viewer.setSource(QUrl.fromLocalFile(src_dir / 'main.qml'))
    viewer.setResizeMode(QQuickView.SizeRootObjectToView)
    viewer.show()

    sys.exit(app.exec())
