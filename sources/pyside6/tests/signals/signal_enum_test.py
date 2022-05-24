# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from enum import Enum
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))

from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal, Slot


class Colors(Enum):
    red = 1
    green = 2
    blue = 3


class Obj(QObject):
    enum_signal = Signal(Colors)
    object_signal = Signal(object)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.enum_signal.connect(self.get_result)
        self.object_signal.connect(self.get_result)
        self.value = -1

    @Slot()
    def get_result(self, i):
        self.value = i


class SignalEnumTests(unittest.TestCase):
    '''Test Signal with enum.Enum'''

    def testSignal(self):
        o = Obj()
        # Default value
        self.assertEqual(o.value, -1)

        # Enum Signal
        o.enum_signal.emit(Colors.green)
        self.assertEqual(o.value, Colors.green)

        # object Signal
        o.object_signal.emit(Colors.red)
        self.assertEqual(o.value, Colors.red)


if __name__ == '__main__':
    unittest.main()
