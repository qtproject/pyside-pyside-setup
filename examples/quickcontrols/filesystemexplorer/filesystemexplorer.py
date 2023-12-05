# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""
This example shows how to customize Qt Quick Controls by implementing a simple filesystem explorer.
"""

# Compile both resource files app.qrc and icons.qrc and include them here if you wish
# to load them from the resource system. Currently, all resources are loaded locally
# import FileSystemModule.rc_icons
# import FileSystemModule.rc_app

from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import (QQmlApplicationEngine, QmlElement, QmlSingleton)
from PySide6.QtCore import (Slot, QFile, QTextStream, QMimeDatabase, QFileInfo, QStandardPaths)

import sys


QML_IMPORT_NAME = "FileSystemModule"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class FileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setRootPath(QStandardPaths.writableLocation(QStandardPaths.HomeLocation))
        self.db = QMimeDatabase()

    # we only need one column in this example
    def columnCount(self, parent):
        return 1

    # check for the correct mime type and then read the file.
    # returns the text file's content or an error message on failure
    @Slot(str, result=str)
    def readFile(self, path):
        if path == "":
            return ""

        file = QFile(path)

        mime = self.db.mimeTypeForFile(QFileInfo(file))
        if ('text' in mime.comment().lower()
                or any('text' in s.lower() for s in mime.parentMimeTypes())):
            if file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(file).readAll()
                return stream
            else:
                return self.tr("Error opening the file!")
        return self.tr("File type not supported!")


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("QtProject")
    app.setApplicationName("File System Explorer")
    engine = QQmlApplicationEngine()
    # Include the path of this file to search for the 'qmldir' module
    engine.addImportPath(sys.path[0])

    engine.loadFromModule("FileSystemModule", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
