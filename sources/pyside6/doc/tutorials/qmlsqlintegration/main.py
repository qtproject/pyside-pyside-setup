# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
import logging

from PySide6.QtCore import QCoreApplication, QDir, QFile, QStandardPaths
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtSql import QSqlDatabase

# We import the file just to trigger the QmlElement type registration.
import sqlDialog  # noqa E703

logging.basicConfig(filename="chat.log", level=logging.DEBUG)
logger = logging.getLogger("logger")


def connectToDatabase():
    database = QSqlDatabase.database()
    if not database.isValid():
        database = QSqlDatabase.addDatabase("QSQLITE")
        if not database.isValid():
            logger.error("Cannot add database")

    app_data = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    write_dir = QDir(app_data)
    if not write_dir.mkpath("."):
        logger.error(f"Failed to create writable directory {app_data}")

    # Ensure that we have a writable location on all devices.
    abs_path = write_dir.absolutePath()
    filename = f"{abs_path}/chat-database.sqlite3"

    # When using the SQLite driver, open() will create the SQLite
    # database if it doesn't exist.
    database.setDatabaseName(filename)
    if not database.open():
        logger.error("Cannot open database")
        QFile.remove(filename)


if __name__ == "__main__":
    app = QGuiApplication()
    QCoreApplication.setOrganizationName("QtProject")
    QCoreApplication.setApplicationName("Chat Tutorial")

    connectToDatabase()

    engine = QQmlApplicationEngine()
    engine.addImportPath(sys.path[0])
    engine.loadFromModule("Main", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    app.exec()
    del engine
