#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QLineF'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QLineF, QPointF


class TestQLineF (unittest.TestCase):
    def testIntersect(self):
        l1 = QLineF(0, 0, 1, 0)
        l2 = QLineF(1, -1, 1, 1)
        tuple_ = l1.intersects(l2)
        self.assertEqual(tuple, tuple_.__class__)
        (value, p) = tuple_
        self.assertEqual(QLineF.BoundedIntersection, value)
        self.assertEqual(QPointF(1, 0), p)


if __name__ == '__main__':
    unittest.main()
