# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL


class MyObject(QObject):
    pass


class TestSignalLimitless(unittest.TestCase):
    SIGNAL_MAX = 100

    def test100DynamicSignals(self):

        self.count = 0

        def onSignal():
            self.count += 1

        # create 100 dynamic signals
        o = MyObject()
        for i in range(self.SIGNAL_MAX):
            o.connect(SIGNAL(f'sig{i}()'), onSignal)

        # check if the signals are valid
        m = o.metaObject()
        for i in range(self.SIGNAL_MAX):
            self.assertTrue(m.indexOfSignal(f'sig{i}()') > 0)

        # emit all 100 signals
        for i in range(self.SIGNAL_MAX):
            o.emit(SIGNAL(f'sig{i}()'))

        self.assertEqual(self.count, self.SIGNAL_MAX)


if __name__ == '__main__':
    unittest.main()
