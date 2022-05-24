# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import qAbs


class QAbsTest(unittest.TestCase):
    '''Tests for qAbs'''

    def testBasic(self):
        def check(x):
            self.assertEqual(qAbs(x), abs(x))

        check(0)
        check(-10)
        check(10)
        check(10.5)
        check(-10.5)


if __name__ == '__main__':
    unittest.main()
