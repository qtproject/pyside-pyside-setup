# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Qt, Slot, Signal


class Receiver(QObject):
    def __init__(self):
        super().__init__()
        self.result = 0

    @Slot(Qt.Alignment, str)
    def handler(self, e, s):
        print('handler', e, "type=", type(e).__name__, s)
        self.result += 1


class Sender(QObject):
    test_sig = Signal(Qt.AlignmentFlag, str)

    def __init__(self):
        super().__init__()

    def emit_test_sig(self):
        self.test_sig.emit(Qt.AlignLeft, "bla")


class TestSignalNewEnum(unittest.TestCase):
    """Test for PYSIDE-2095, signals with new enums in Python 3.11."""

    def testIt(self):
        sender = Sender()
        receiver = Receiver()
        sender.test_sig.connect(receiver.handler)

        sender.emit_test_sig()
        self.assertEqual(receiver.result, 1)


if __name__ == '__main__':
    unittest.main()
