#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QSize'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QSize


class QSizeOperator(unittest.TestCase):
    def testOperatorMultiply(self):
        # QSize operator * float
        # bug 131
        a = QSize(1, 1)
        x = a * 3.4
        self.assertEqual(QSize(3, 3), x)

    def testOperatorRevertedMultiply(self):
        # QSize operator * float, reverted
        # bug 132
        a = QSize(1, 1)
        x = 3.4 * a
        self.assertEqual(QSize(3, 3), x)


if __name__ == '__main__':
    unittest.main()

