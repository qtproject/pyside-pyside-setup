# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QIODevice, QTextStream


class MyDevice(QIODevice):
    def __init__(self, txt):
        super().__init__()
        self.txt = txt
        self.ptr = 0

    def readData(self, size):
        size = min(len(self.txt) - self.ptr, size)
        retval = self.txt[self.ptr:size]
        self.ptr += size
        return retval


class QIODeviceTest(unittest.TestCase):

    def testIt(self):
        device = MyDevice("hello world\nhello again")
        device.open(QIODevice.ReadOnly)

        s = QTextStream(device)
        self.assertEqual(s.readLine(), "hello world")
        self.assertEqual(s.readLine(), "hello again")


if __name__ == '__main__':
    unittest.main()
