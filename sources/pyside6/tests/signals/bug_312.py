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

MAX_LOOPS = 5
MAX_OBJECTS = 200


class Sender(QObject):
    fire = Signal()


class MultipleSlots(unittest.TestCase):
    def myCB(self):
        self._count += 1

    def testDisconnectCleanup(self):
        for c in range(MAX_LOOPS):
            self._count = 0
            self._senders = []
            for i in range(MAX_OBJECTS):
                o = Sender()
                o.fire.connect(lambda: self.myCB())
                self._senders.append(o)
                o.fire.emit()

            self.assertEqual(self._count, MAX_OBJECTS)

            # delete all senders will disconnect the signals
            self._senders = []


if __name__ == '__main__':
    unittest.main()
