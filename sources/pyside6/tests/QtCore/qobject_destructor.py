# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject


class MyObject(QObject):
    def __init__(self, other=None):
        super().__init__(None)
        self._o = other


class TestDestructor(unittest.TestCase):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReference(self):
        o = QObject()
        m = MyObject(o)
        self.assertEqual(sys.getrefcount(o), 3)
        del m
        self.assertEqual(sys.getrefcount(o), 2)


if __name__ == '__main__':
    unittest.main()
