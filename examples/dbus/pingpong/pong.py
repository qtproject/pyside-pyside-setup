# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the QtDBus pingpong example from Qt v6.x (pong server)"""

import sys
from PySide6.QtCore import QCoreApplication, QObject, Slot
from PySide6.QtDBus import QDBusConnection


SERVICE_NAME = "org.example.QtDBus.PingExample"


class Pong(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str, result=str)
    def ping(self, arg):
        print(f'pong: Received ping({arg})')
        qApp.quit()  # noqa: F821
        return f'ping("{arg}") got called'


if __name__ == "__main__":
    app = QCoreApplication()
    session_bus = QDBusConnection.sessionBus()
    if not session_bus.isConnected():
        print("Cannot connect to the D-Bus session bus.\n"
              "To start it, run:\n"
              "\teval `dbus-launch --auto-syntax`\n")
        sys.exit(-1)

    if not session_bus.registerService(SERVICE_NAME):
        print(session_bus.lastError().message())
        sys.exit(-1)

    pong = Pong()
    session_bus.registerObject('/', pong, QDBusConnection.ExportAllSlots)

    print(f'pong: {SERVICE_NAME} running. Now start ping.py')
    exit_code = app.exec()
    print('pong: terminating')
    sys.exit(exit_code)
