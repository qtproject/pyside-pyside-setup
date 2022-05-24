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


class MyIODevice (QIODevice):
    def readData(self, amount):
        return bytes("\0a" * int(amount / 2), "UTF-8")

    def readLineData(self, maxSize):
        return bytes("\0b" * 4, "UTF-8")

    def atEnd(self):
        return False


class TestBug944 (unittest.TestCase):

    def testIt(self):
        device = MyIODevice()
        device.open(QIODevice.ReadOnly)
        s = QTextStream(device)
        self.assertEqual(s.read(4), "\0a\0a")
        self.assertEqual(device.readLine(), "\0b\0b\0b\0b")


if __name__ == "__main__":
    unittest.main()
