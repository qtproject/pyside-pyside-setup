# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Slot, QMetaObject


class MyObject(QObject):
    @Slot(int, str)
    def slot1(self, a, b):
        pass


class testAttribute(unittest.TestCase):
    def testBug896(self):
        mo = MyObject.staticMetaObject
        self.assertTrue(isinstance(mo, QMetaObject))
        self.assertEqual(mo.className(), 'MyObject')
        self.assertTrue(mo.indexOfSlot('slot1(int,QString)') > -1)

    def testDuplicateSlot(self):
        mo = MyObject.staticMetaObject
        self.assertEqual(mo.indexOfSignal('destroyed(void)'), -1)
        self.assertTrue(mo.indexOfSignal('destroyed()') > -1)


if __name__ == '__main__':
    unittest.main()
