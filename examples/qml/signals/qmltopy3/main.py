# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
from pathlib import Path
import sys
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView


def sayThis(s):
    print(s)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    qml_file = os.fspath(Path(__file__).resolve().parent / 'view.qml')
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Status.Error:
        sys.exit(-1)

    root = view.rootObject()
    root.textRotationChanged.connect(sayThis)
    root.buttonClicked.connect(lambda: sayThis("clicked button (QML top-level signal)"))

    view.show()
    res = app.exec()
    # Deleting the view before it goes out of scope is required to make sure all child QML instances
    # are destroyed in the correct order.
    del view
    sys.exit(res)
