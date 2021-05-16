# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QDBus'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

import sys
from PySide6.QtCore import QCoreApplication
from PySide6.QtDBus import (QDBusConnection, QDBusConnectionInterface,
                            QDBusInterface, QDBusReply)


def service_names():
    session_bus = QDBusConnection.sessionBus()
    if not QDBusConnection.sessionBus().isConnected():
        print("Cannot connect to the D-Bus session bus.", file=sys.stderr)
        return []
    reply = session_bus.interface().registeredServiceNames()
    if not reply.isValid():
        print("Error:", reply.error().message(), file=sys.stderr)
        return []
    return reply.value()


class TestDBus(UsesQApplication):
    '''Simple Test case for QDBus'''

    def test_service_names(self):
        names = service_names()
        print(names)


if __name__ == '__main__':
    unittest.main()
