#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for PYSIDE-344, imul/idiv are used instead of mul/div, modifying the argument passed in'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QMargins, QPoint, QPointF, QSize, QSizeF
from PySide6.QtGui import (QMatrix4x4, QQuaternion, QTransform, QVector2D,
                           QVector3D, QVector4D)


def testList():
    return [QPoint(10, 10), QPointF(1, 1), QSize(10, 10), QSizeF(1, 1),
            QMargins(10, 10, 10, 10),
            QTransform(), QMatrix4x4(),
            QVector2D(1, 1), QVector3D(1, 1, 1), QVector4D(1, 1, 1, 1),
            QQuaternion(1, 1, 1, 1)]


class TestMulDiv(unittest.TestCase):

    def testMultiplication(self):
        fails = ''
        for a in testList():
            mul = (a * 2)
        if a == mul:
            fails += ' ' + type(a).__name__
        self.assertEqual(fails, '')

    def testDivision(self):
        fails = ''
        for a in testList():
            div = (a * 2)
            if a == div:
                fails += ' ' + type(a).__name__
        self.assertEqual(fails, '')


if __name__ == '__main__':
    unittest.main()
