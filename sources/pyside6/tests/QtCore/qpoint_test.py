# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QPoint and QPointF'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QPoint, QPointF


class QPointTest(unittest.TestCase):

    def testQPointCtor(self):
        point = QPoint(QPoint(10, 20))


class QPointFTest(unittest.TestCase):

    def testQPointFCtor(self):
        pointf = QPointF(QPoint(10, 20))


if __name__ == '__main__':
    unittest.main()

