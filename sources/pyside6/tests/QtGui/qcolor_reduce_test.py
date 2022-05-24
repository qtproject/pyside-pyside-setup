# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import pickle
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QColor


class TestQColor (unittest.TestCase):
    def reduceColor(self, c):
        p = pickle.dumps(c)
        c2 = pickle.loads(p)
        self.assertEqual(c.spec(), c2.spec())
        self.assertEqual(c, c2)

    def testReduceEmpty(self):
        self.reduceColor(QColor())

    def testReduceString(self):
        self.reduceColor(QColor('gray'))

    def testReduceRGB(self):
        self.reduceColor(QColor.fromRgbF(0.1, 0.2, 0.3, 0.4))

    def testReduceCMYK(self):
        self.reduceColor(QColor.fromCmykF(0.1, 0.2, 0.3, 0.4, 0.5))

    def testReduceHsl(self):
        self.reduceColor(QColor.fromHslF(0.1, 0.2, 0.3, 0.4))

    def testReduceHsv(self):
        self.reduceColor(QColor.fromHsvF(0.1, 0.2, 0.3, 0.4))


if __name__ == "__main__":
    unittest.main()
