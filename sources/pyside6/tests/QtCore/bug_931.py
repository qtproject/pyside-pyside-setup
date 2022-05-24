# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal
o = QObject()


class MyObject(QObject):
    s = Signal(int)


class CheckSignalType(unittest.TestCase):
    def testSignal(self):
        self.assertTrue(isinstance(QObject.destroyed, Signal))
        self.assertEqual(type(QObject.destroyed), Signal)

        self.assertEqual(type(o.destroyed).__name__, "SignalInstance")
        self.assertNotEqual(type(o.destroyed), Signal)

        self.assertTrue(isinstance(o.destroyed, Signal))
        self.assertTrue(isinstance(MyObject.s, Signal))
        self.assertFalse(isinstance(int, Signal))


if __name__ == '__main__':
    unittest.main()
