# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the QtDBus listnames example from Qt v6.x"""

import sys
from PySide6.QtCore import QCoreApplication
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusReply


def method1():
    print("Method 1:")

    session_bus = QDBusConnection.sessionBus()
    reply = session_bus.interface().registeredServiceNames()
    if not reply.isValid():
        print("Error:", reply.error().message())
        sys.exit(1)
    values = reply.value()
    for name in values:
        print(name)


def method2():
    print("Method 2:")

    session_bus = QDBusConnection.sessionBus()
    dbus_iface = QDBusInterface("org.freedesktop.DBus", "/org/freedesktop/DBus",
                                "org.freedesktop.DBus", session_bus)
    message = dbus_iface.call("ListNames")
    reply = QDBusReply(message)
    print(reply.value())


def method3():
    print("Method 3:")
    session_bus = QDBusConnection.sessionBus()
    print(session_bus.interface().registeredServiceNames().value())


if __name__ == "__main__":
    app = QCoreApplication()

    if not QDBusConnection.sessionBus().isConnected():
        print("Cannot connect to the D-Bus session bus.\n"
              "To start it, run:\n"
              "\teval `dbus-launch --auto-syntax`\n",
              file=sys.stderr)
        sys.exit(1)

    method1()
    method2()
    method3()
