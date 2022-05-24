# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Property


class MyObject(QObject):
    def __init__(self):
        super().__init__()
        self._value = None

    @Property(int)
    def value(self):
        return self._value

    @value.setter
    # Note: The name of property and setter must be the same, because the
    # object changes its identity all the time. `valueSet` no longer works.
    def value(self, value):
        self._value = value


class PropertyTest(unittest.TestCase):
    def destroyCB(self, obj):
        self._obDestroyed = True

    def testDecorator(self):
        self._obDestroyed = False
        o = MyObject()
        weak = weakref.ref(o, self.destroyCB)
        o.value = 10
        self.assertEqual(o._value, 10)
        self.assertEqual(o.value, 10)
        del o
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertTrue(self._obDestroyed)


if __name__ == '__main__':
    unittest.main()
