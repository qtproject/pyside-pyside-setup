# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication


from PySide6.QtCore import QCoreApplication, QObject  # noqa: F401
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType


class BaseClass(QObject):
    def __init__(self, p=None):
        super().__init__(p)


class ChildClass(BaseClass):
    def __init__(self, p=None):
        super().__init__(p)


class TestQmlRegisterType(UsesQApplication):
    """Test the legacy QML register functions."""

    def test(self):
        qmlRegisterType(BaseClass, 'test', 1, 0, 'BaseClass')
        qmlRegisterType(ChildClass, 'test', 1, 0, 'ChildClass')
        # PYSIDE-2709: qmlRegisterType() would set additional class info
        # on the meta objects for registration which caused another meta
        # object to be created, breaking inheritance.
        child = ChildClass()
        base = BaseClass()
        self.assertTrue(child.metaObject().inherits(base.metaObject()))

        engine = QQmlApplicationEngine()
        file = Path(__file__).resolve().parent / 'qmlregistertype_test.qml'

        engine.load(file)
        rootObjects = engine.rootObjects()
        self.assertTrue(rootObjects)
        self.assertTrue(type(rootObjects[0]), ChildClass)


if __name__ == '__main__':
    unittest.main()
