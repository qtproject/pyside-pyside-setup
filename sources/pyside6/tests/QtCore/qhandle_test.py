#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QEnum and QFlags'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QThread, Qt


class TestHANDLE(unittest.TestCase):
    def testIntConversion(self):
        i = 0
        h = QThread.currentThreadId()
        i = 0 + int(h)
        self.assertEqual(i, int(h))


if __name__ == '__main__':
    unittest.main()
