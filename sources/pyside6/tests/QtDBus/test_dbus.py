#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

'''Test cases for QDBus'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqcoreapplication import UsesQCoreApplication

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


class TestDBus(UsesQCoreApplication):
    '''Simple Test case for QDBus'''

    def test_service_names(self):
        names = service_names()
        print(names)


if __name__ == '__main__':
    unittest.main()
