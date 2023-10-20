# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""
PySide6 port of Qt Quick Controls Contact List example from Qt v6.x
"""
import sys
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from contactmodel import ContactModel

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("QtProject")
    app.setApplicationName("ContactsList")
    engine = QQmlApplicationEngine()

    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("Contact", "ContactList")

    if not engine.rootObjects():
        sys.exit(-1)

    del engine
    sys.exit(app.exec())
