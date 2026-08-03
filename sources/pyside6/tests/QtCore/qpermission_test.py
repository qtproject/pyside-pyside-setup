# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCameraPermission, QCoreApplication, QObject
from helper.usesqapplication import UsesQApplication


def on_permission(permission) -> None:
    print('on_permission', permission.status())
    QCoreApplication.quit()


class Receiver(QObject):
    def on_permission(self, permission):
        print('Receiver.on_permission()', permission.status())
        QCoreApplication.quit()


class TestQPermission(UsesQApplication):
    def testFreeFunction(self):
        app = qApp  # noqa: F821
        app.requestPermission(QCameraPermission(), app, on_permission)
        app.exec()

    def testMember(self):
        app = qApp  # noqa: F821
        receiver = Receiver()
        app.requestPermission(QCameraPermission(), receiver, receiver.on_permission)
        app.exec()


if __name__ == '__main__':
    unittest.main()
