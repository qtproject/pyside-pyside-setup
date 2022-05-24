# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for Reference count when the object is created in c++ side'''

import gc
import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPolygonF
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsRectItem

from helper.usesqapplication import UsesQApplication

destroyedRect = False
destroyedPol = False


def rect_del(o):
    global destroyedRect
    destroyedRect = True


def pol_del(o):
    global destroyedPol
    destroyedPol = True


class ReferenceCount(UsesQApplication):

    def setUp(self):
        super(ReferenceCount, self).setUp()
        self.scene = QGraphicsScene()

    def tearDown(self):
        super(ReferenceCount, self).tearDown()

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def beforeTest(self):
        points = [QPointF(0, 0), QPointF(100, 100), QPointF(0, 100)]
        pol = self.scene.addPolygon(QPolygonF(points))
        self.assertTrue(isinstance(pol, QGraphicsPolygonItem))
        self.wrp = weakref.ref(pol, pol_del)

        # refcount need be 3 because one ref for QGraphicsScene, and one to rect obj
        self.assertEqual(sys.getrefcount(pol), 3)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReferenceCount(self):
        global destroyedRect
        global destroyedPol

        self.beforeTest()

        rect = self.scene.addRect(10.0, 10.0, 10.0, 10.0)
        self.assertTrue(isinstance(rect, QGraphicsRectItem))

        self.wrr = weakref.ref(rect, rect_del)

        # refcount need be 3 because one ref for QGraphicsScene, and one to rect obj
        self.assertEqual(sys.getrefcount(rect), 3)

        del rect
        # not destroyed because one ref continue in QGraphicsScene
        self.assertEqual(destroyedRect, False)
        self.assertEqual(destroyedPol, False)

        del self.scene

        # QGraphicsScene was destroyed and this destroy internal ref to rect
        self.assertEqual(destroyedRect, True)
        self.assertEqual(destroyedPol, True)


if __name__ == '__main__':
    unittest.main()
