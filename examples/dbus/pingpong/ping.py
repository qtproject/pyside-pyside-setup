# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the QtDBus pingpong example from Qt v6.x (ping client)"""

import sys
from PySide6.QtCore import QCoreApplication
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusReply


SERVICE_NAME = 'org.example.QtDBus.PingExample'


if __name__ == "__main__":
    app = QCoreApplication()
    session_bus = QDBusConnection.sessionBus()
    if not session_bus.isConnected():
        print("Cannot connect to the D-Bus session bus.\n"
              "To start it, run:\n"
              "\teval `dbus-launch --auto-syntax`\n")
        sys.exit(-1)

    iface = QDBusInterface(SERVICE_NAME, '/', '', session_bus)
    if not iface.isValid():
        print(session_bus.lastError().message())
        sys.exit(-1)

    argument = sys.argv[1] if len(sys.argv) > 1 else 'Hello'
    message = iface.call('ping', argument)
    reply = QDBusReply(message)
    if not reply.isValid():
        error = reply.error().message()
        print(f'ping: Call failed: {error}')
        sys.exit(-1)

    value = reply.value()
    print(f'ping: Reply was: {value}')
    sys.exit(0)
