# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import QObject
from testbinding import TestObject


class Receiver(QObject):

    def __init__(self):
        super().__init__()
        self.received = None

    def slot(self, value):
        self.received = value


class TypedefSignal(unittest.TestCase):

    def testTypedef(self):
        obj = TestObject(0)
        receiver = Receiver()

        obj.signalWithTypedefValue.connect(receiver.slot)
        obj.emitSignalWithTypedefValue(2)
        self.assertEqual(receiver.received.value, 2)


if __name__ == '__main__':
    unittest.main()
