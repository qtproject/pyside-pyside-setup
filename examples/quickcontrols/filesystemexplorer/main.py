# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""
This example shows how to customize Qt Quick Controls by implementing a simple filesystem explorer.
"""

# Compile both resource files app.qrc and icons.qrc and include them here if you wish
# to load them from the resource system. Currently, all resources are loaded locally
# import FileSystemModule.rc_icons
# import FileSystemModule.rc_app

from editormodels import FileSystemModel  # noqa: F401
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QCommandLineParser, qVersion

import sys

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("QtProject")
    app.setApplicationName("File System Explorer")
    app.setApplicationVersion(qVersion())
    app.setWindowIcon(QIcon(sys.path[0] + "/FileSystemModule/icons/app_icon.svg"))

    parser = QCommandLineParser()
    parser.setApplicationDescription("Qt Filesystemexplorer Example")
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument("", "Initial directory", "[path]")
    parser.process(app)
    args = parser.positionalArguments()

    engine = QQmlApplicationEngine()
    # Include the path of this file to search for the 'qmldir' module
    engine.addImportPath(sys.path[0])

    engine.loadFromModule("FileSystemModule", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    if (len(args) == 1):
        fsm = engine.singletonInstance("FileSystemModule", "FileSystemModel")
        fsm.setInitialDirectory(args[0])

    sys.exit(app.exec())
