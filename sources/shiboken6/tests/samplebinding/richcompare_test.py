#!/usr/bin/env python
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

class TestRichCompare(unittest.TestCase):

    def testIt(self):
        a = Expression(2)
        b = Expression(3)
        c = a + b
        d = a + c < b + a
        self.assertEqual(d.toString(), "((2+(2+3))<(3+2))")

if __name__ == '__main__':
    unittest.main()
