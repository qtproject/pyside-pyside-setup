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

from sample import Color, Brush

class TestNonZeroOperator(unittest.TestCase):
    def testColor(self):
        """Color has a Qt-style isNull()"""
        c = Color()
        self.assertFalse(c)
        c = Color(2)
        self.assertTrue(c)

    def testBrush(self):
        """Brush enables its operator bool in the typesystem XML"""
        b = Brush()
        self.assertFalse(b)
        b = Brush(Color(2))
        self.assertTrue(b)


if __name__ == "__main__":
    unittest.main()
