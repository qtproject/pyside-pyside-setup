# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *


class TestNewDivision(unittest.TestCase):

    def testIt(self):
        p = Point(4, 4)
        p2 = p/2
        self.assertEqual(p2, Point(2, 2))

if __name__ == "__main__":
    unittest.main()

