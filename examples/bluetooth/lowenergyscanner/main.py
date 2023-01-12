# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the bluetooth/lowenergyscanner example from Qt v6.x"""


import sys
import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView

from device import Device
from pathlib import Path

import rc_resources

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    d = Device()
    view = QQuickView()
    view.rootContext().setContextProperty("device", d)
    src_dir = Path(__file__).resolve().parent
    view.engine().addImportPath(os.fspath(src_dir))
    view.engine().quit.connect(view.close)
    view.setSource(QUrl.fromLocalFile(":/assets/main.qml"))
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.show()
    res = app.exec()
    del view
    sys.exit(res)

