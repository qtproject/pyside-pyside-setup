#!/usr/bin/env python
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


class Sender(QObject):
    the_signal = Signal(int, int, int)


class ArgsDontMatch(unittest.TestCase):

    def callback(self, arg1):
        self.ok = True

    def testConnectSignalToSlotWithLessArgs(self):
        self.ok = False
        obj1 = Sender()
        obj1.the_signal.connect(self.callback)
        obj1.the_signal.emit(1, 2, 3)

        self.assertTrue(self.ok)


if __name__ == '__main__':
    unittest.main()
