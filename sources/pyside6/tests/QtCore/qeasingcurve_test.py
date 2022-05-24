# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest
import gc

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QEasingCurve


def myFunction(progress):
    if progress == 1.0:
        return 100.0
    else:
        return -100.0


class TestQEasingCurve(unittest.TestCase):
    def testCustomType(self):
        ec = QEasingCurve()
        ec.setCustomType(myFunction)
        self.assertEqual(ec.valueForProgress(1.0), 100.0)
        self.assertEqual(ec.valueForProgress(0.5), -100.0)

    def testObjectCleanup(self):
        for i in range(100):
            ec = QEasingCurve()
            ec.setCustomType(myFunction)
            self.assertEqual(ec.valueForProgress(1.0), 100.0)
            self.assertEqual(ec.valueForProgress(0.5), -100.0)
            # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
            gc.collect()


if __name__ == '__main__':
    unittest.main()
