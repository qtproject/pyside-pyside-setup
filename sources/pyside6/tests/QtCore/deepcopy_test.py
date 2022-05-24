# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from copy import deepcopy
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray, QDate, QDateTime, QTime, QLine, QLineF
from PySide6.QtCore import Qt, QSize, QSizeF, QRect, QRectF, QDir, QPoint, QPointF
try:
    from PySide6.QtCore import QUuid
    HAVE_Q = True
except ImportError:
    HAVE_Q = False


class DeepCopyHelper:
    def testCopy(self):
        copy = deepcopy([self.original])[0]
        self.assertTrue(copy is not self.original)
        self.assertEqual(copy, self.original)


class QByteArrayDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QByteArray(bytes('the quick brown fox jumps over the lazy dog', "UTF-8"))


class QDateDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QDate(2010, 11, 22)


class QTimeDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QTime(11, 37, 55, 692)


class QDateTimeDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QDateTime(2010, 5, 18, 10, 24, 45, 223, Qt.LocalTime)


class QSizeDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QSize(42, 190)


class QSizeFDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QSizeF(42.7, 190.2)


class QRectDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QRect(100, 200, 300, 400)


class QRectFDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QRectF(100.33, 200.254, 300.321, 400.123)


class QLineDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QLine(1, 2, 3, 4)


class QLineFDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QLineF(1.1, 2.2, 3.3, 4.4)


class QPointDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QPoint(1, 2)


class QPointFDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QPointF(1.1, 2.2)


class QDirDeepCopy(DeepCopyHelper, unittest.TestCase):
    def setUp(self):
        self.original = QDir("./")


class QUuiCopy(DeepCopyHelper, unittest.TestCase):
    @unittest.skipUnless(HAVE_Q, "QUuid is currently not supported on this platform.")
    def setUp(self):
        self.original = QUuid("67C8770B-44F1-410A-AB9A-F9B5446F13EE")


if __name__ == '__main__':
    unittest.main()
