# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import TestObject
from PySide6.QtCore import QObject


class ListConnectionTest(unittest.TestCase):

    def childrenChanged(self, children):
        self._child = children[0]

    def testConnection(self):
        o = TestObject(0)
        c = QObject()
        c.setObjectName("child")
        self._child = None
        o.childrenChanged.connect(self.childrenChanged)
        o.addChild(c)
        self.assertEqual(self._child.objectName(), "child")


if __name__ == '__main__':
    unittest.main()

