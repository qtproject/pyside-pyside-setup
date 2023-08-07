# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Property, QObject
from PySide6.QtQml import QQmlComponent


class WithComponent(QObject):
    def get_component(self):
        return None

    component = Property(QQmlComponent, fget=get_component)


class TestQmlSupport(unittest.TestCase):

    def testMetatypeValid(self):
        m = WithComponent.staticMetaObject
        c = m.property(m.indexOfProperty("component"))

        self.assertTrue(c.typeId() > 0)
        self.assertTrue(c.typeName() == "QQmlComponent*")
        self.assertTrue(c.metaType().isValid())


if __name__ == '__main__':
    unittest.main()
