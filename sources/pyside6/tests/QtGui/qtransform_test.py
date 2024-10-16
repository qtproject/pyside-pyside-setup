# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QPointF
from PySide6.QtGui import QTransform, QPolygonF, QPolygonF, QQuaternion, QVector3D


class QTransformTest(unittest.TestCase):

    def testMap(self):
        transform = QTransform()
        values = (10.0, 20.0)
        tx, ty = transform.map(*values)
        self.assertTrue(isinstance(tx, float))
        self.assertTrue(isinstance(ty, float))
        self.assertEqual((tx, ty), values)

    def testquadToQuad(self):
        q1 = QPolygonF()
        q1.append(QPointF(10.0, 10.0))
        q1.append(QPointF(20.0, 10.0))
        q1.append(QPointF(10.0, -10.0))
        q1.append(QPointF(20.0, -10.0))

        q2 = QPolygonF()
        q2.append(QPointF(20.0, 20.0))
        q2.append(QPointF(30.0, 20.0))
        q2.append(QPointF(20.0, -20.0))
        q2.append(QPointF(30.0, -20.0))

        t1 = QTransform()
        r1 = QTransform.quadToQuad(q1, q2, t1)
        r2 = QTransform.quadToQuad(q1, q2)

        self.assertTrue(r1)
        self.assertTrue(r2)

        self.assertEqual(t1, r2)

    def testquadToSquare(self):
        q1 = QPolygonF()
        q1.append(QPointF(10.0, 10.0))
        q1.append(QPointF(20.0, 10.0))
        q1.append(QPointF(10.0, -10.0))
        q1.append(QPointF(20.0, -10.0))

        t1 = QTransform()
        r1 = QTransform.quadToSquare(q1, t1)
        r2 = QTransform.quadToSquare(q1)

        self.assertTrue(r1)
        self.assertTrue(r2)

        self.assertEqual(t1, r2)

    def testsquareToQuad(self):
        q1 = QPolygonF()
        q1.append(QPointF(10.0, 10.0))
        q1.append(QPointF(20.0, 10.0))
        q1.append(QPointF(10.0, -10.0))
        q1.append(QPointF(20.0, -10.0))

        t1 = QTransform()
        r1 = QTransform.squareToQuad(q1, t1)
        r2 = QTransform.squareToQuad(q1)

        self.assertTrue(r1)
        self.assertTrue(r2)

        self.assertEqual(t1, r2)

    def testQQuaternion(self):
        """Test return tuples."""
        q = QQuaternion(1, 1, 1, 1)
        self.assertEqual(len(q.getAxisAndAngle()), 2)
        self.assertEqual(len(q.getEulerAngles()), 3)


if __name__ == "__main__":
    unittest.main()

