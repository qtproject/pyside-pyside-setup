# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the location/mapviewer example from Qt v6.x"""

import os
import sys
from pathlib import Path

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QSslSocket
from PySide6.QtCore import QCoreApplication, QMetaObject, Q_ARG

HELP = """Usage:
plugin.<parameter_name> <parameter_value> - Sets parameter = value for plugin"""


def parseArgs(args):
    parameters = {}
    while args:
        param = args[0]
        args = args[1:]
        if param.startswith("--plugin."):
            param = param[9:]
            if not args or args[0].startswith("--"):
                parameters[param] = True
            else:
                value = args[0]
                args = args[1:]
                if value in ("true", "on", "enabled"):
                    parameters[param] = True
                elif value in ("false", "off", "disable"):
                    parameters[param] = False
                else:
                    parameters[param] = value
    return parameters


if __name__ == "__main__":
    additionalLibraryPaths = os.environ.get("QTLOCATION_EXTRA_LIBRARY_PATH")
    if additionalLibraryPaths:
        for p in additionalLibraryPaths.split(':'):
            QCoreApplication.addLibraryPath(p)

    application = QGuiApplication(sys.argv)
    name = "QtLocation Mapviewer example"
    QCoreApplication.setApplicationName(name)

    args = sys.argv[1:]
    if "--help" in args:
        print(f"{name}\n\n{HELP}")
        sys.exit(0)

    parameters = parseArgs(args)
    if not parameters.get("osm.useragent"):
        parameters["osm.useragent"] = name

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("supportsSsl",
                                            QSslSocket.supportsSsl())
    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("MapViewer", "Main")
    engine.quit.connect(QCoreApplication.quit)

    items = engine.rootObjects()
    if not items:
        sys.exit(-1)

    QMetaObject.invokeMethod(items[0], "initializeProviders",
                             Q_ARG("QVariant", parameters))

    ex = application.exec()
    del engine
    sys.exit(ex)
