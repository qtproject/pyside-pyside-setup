# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import logging

from PySide6.QtCore import QDir, QFile, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtSql import QSqlDatabase

# We import the file just to trigger the QmlElement type registration.
import sqlDialog

logging.basicConfig(filename="chat.log", level=logging.DEBUG)
logger = logging.getLogger("logger")


def connectToDatabase():
    database = QSqlDatabase.database()
    if not database.isValid():
        database = QSqlDatabase.addDatabase("QSQLITE")
        if not database.isValid():
            logger.error("Cannot add database")

    write_dir = QDir("")
    if not write_dir.mkpath("."):
        logger.error("Failed to create writable directory")

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
    connectToDatabase()

    engine = QQmlApplicationEngine()
    engine.load(QUrl("chat.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    app.exec()
