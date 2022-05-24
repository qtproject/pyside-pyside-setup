# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QRadialGradient
from PySide6.QtCore import QPointF


class QRadialGradientConstructor(unittest.TestCase):
    def _compare(self, qptf, tpl):
        self.assertEqual((qptf.x(), qptf.y()), tpl)

    def _assertValues(self, grad):
        self._compare(grad.center(), (1.0, 2.0))
        self._compare(grad.focalPoint(), (3.0, 4.0))
        self.assertEqual(grad.radius(), 5.0)

    def testAllInt(self):
        grad = QRadialGradient(1, 2, 5, 3, 4)
        self._assertValues(grad)

    def testQPointF(self):
        grad = QRadialGradient(QPointF(1, 2), 5, QPointF(3, 4))
        self._assertValues(grad)

    def testSetQPointF(self):
        grad = QRadialGradient()
        grad.setCenter(QPointF(1, 2))
        self._compare(grad.center(), (1.0, 2.0))


if __name__ == '__main__':
    unittest.main()
