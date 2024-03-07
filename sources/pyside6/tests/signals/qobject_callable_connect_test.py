# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal


class Emitter(QObject):
    sig = Signal(int)


class CallableObject(QObject):
    called = False
    x = 0

    def __call__(self, x: int):
        self.called = True
        self.x = x


class QObjectCallableConnectTest(unittest.TestCase):
    '''Test case for QObject.connect() when the callable is also a QObject.'''

    def testCallableConnect(self):
        emitter = Emitter()
        obj = CallableObject()
        x = 1

        emitter.sig.connect(obj)
        emitter.sig.emit(x)

        self.assertTrue(obj.called)
        self.assertEqual(obj.x, x)


if __name__ == '__main__':
    unittest.main()
