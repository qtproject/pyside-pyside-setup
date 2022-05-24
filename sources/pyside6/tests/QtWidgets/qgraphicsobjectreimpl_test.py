# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test cases related to QGraphicsItem and subclasses'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QGraphicsObject, QGraphicsWidget
from PySide6.QtCore import QRectF

from helper.usesqapplication import UsesQApplication


class GObjA(QGraphicsObject):
    def paint(self, *args):
        pass

    def boundingRect(self):
        return QRectF()

    def itemChange(self, *args):
        return QGraphicsObject.itemChange(self, *args)


class GObjB(QGraphicsObject):
    def paint(self, *args):
        pass

    def boundingRect(self):
        return QRectF()


class QGraphicsObjectReimpl(UsesQApplication):
    '''Test case for reimplementing QGraphicsObject'''

    def testReimplementationTypes(self):
        w = QGraphicsWidget()

        # PYSIDE-86:
        #   This case failed because GObjA was reimplementing
        #   the method itemChange() from QGraphicsItem,
        #   and then the QVariant was not associated with
        #   a QGraphicsItem but a QObjectItem because the base
        #   class was a QObject.
        gobjA = GObjA()
        gobjA.setParentItem(w)
        self.assertIs(type(w), type(gobjA.parentItem()))

        gobjB = GObjB()
        gobjB.setParentItem(w)
        self.assertIs(type(w), type(gobjB.parentItem()))


if __name__ == '__main__':
    unittest.main()
