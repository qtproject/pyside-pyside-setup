# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6


class TestVersionInfo(unittest.TestCase):
    def testIt(self):

        v = PySide6.__version_info__
        self.assertEqual(type(v), tuple)
        self.assertEqual(len(v), 5)
        self.assertEqual(type(v[0]), int)
        self.assertEqual(type(v[1]), int)
        self.assertEqual(type(v[2]), int)
        self.assertEqual(type(v[3]), str)
        self.assertEqual(type(v[4]), str)

        self.assertEqual(type(PySide6.__version__), str)


if __name__ == '__main__':
    unittest.main()
