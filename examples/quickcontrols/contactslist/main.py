# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""
PySide6 port of Qt Quick Controls Contact List example from Qt v6.x
"""
import sys
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from contactmodel import ContactModel  # noqa: F401

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("QtProject")
    app.setApplicationName("ContactsList")
    engine = QQmlApplicationEngine()

    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("Contact", "ContactList")

    if not engine.rootObjects():
        sys.exit(-1)

    ex = app.exec()
    del engine
    sys.exit(ex)
