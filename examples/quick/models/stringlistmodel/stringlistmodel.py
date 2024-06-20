# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from pathlib import Path
import sys
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView

# This example illustrates exposing a QStringList as a model in QML

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    dataList = ["Item 1", "Item 2", "Item 3", "Item 4"]

    view = QQuickView()
    view.setInitialProperties({"model": dataList})

    qml_file = Path(__file__).parent / "view.qml"
    view.setSource(QUrl.fromLocalFile(qml_file))
    view.show()

    r = app.exec()
    del view
    sys.exit(r)
