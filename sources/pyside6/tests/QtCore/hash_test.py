#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QDate, QDateTime, QTime, QUrl
from PySide6.QtCore import QLine, QPoint, QRect, QSize


URL = "https://qt.io/"


class HashTest(unittest.TestCase):
    def testInsert(self):
        myHash = {}
        qdate = QDate.currentDate()
        qdatetime = QDateTime.currentDateTime()
        qtime = QTime.currentTime()
        qurl = QUrl(URL)
        self.assertTrue(qurl.isValid())
        qpoint = QPoint(12, 42)

        myHash[qdate] = "QDate"
        myHash[qdatetime] = "QDateTime"
        myHash[qtime] = "QTime"
        myHash[qurl] = "QUrl"
        myHash[qpoint] = "QPoint"

        self.assertEqual(myHash[qdate], "QDate")
        self.assertEqual(myHash[qdatetime], "QDateTime")
        self.assertEqual(myHash[qtime], "QTime")
        self.assertEqual(myHash[qurl], "QUrl")
        self.assertEqual(myHash[qpoint], "QPoint")

    def testQPointHash(self):
        p1 = QPoint(12, 34)
        p2 = QPoint(12, 34)
        self.assertFalse(p1 is p2)
        self.assertEqual(p1, p2)
        self.assertEqual(hash(p1), hash(p2))

    def testQSizeHash(self):
        s1 = QSize(12, 34)
        s2 = QSize(12, 34)
        self.assertFalse(s1 is s2)
        self.assertEqual(s1, s2)
        self.assertEqual(hash(s1), hash(s2))

    def testQRectHash(self):
        r1 = QRect(12, 34, 56, 78)
        r2 = QRect(12, 34, 56, 78)
        self.assertFalse(r1 is r2)
        self.assertEqual(r1, r2)
        self.assertEqual(hash(r1), hash(r2))

    def testQLineHash(self):
        l1 = QLine(12, 34, 56, 78)
        l2 = QLine(12, 34, 56, 78)
        self.assertFalse(l1 is l2)
        self.assertEqual(l1, l2)
        self.assertEqual(hash(l1), hash(l2))

    def testQTimeHash(self):
        t1 = QTime(5, 5, 5)
        t2 = QTime(5, 5, 5)
        self.assertFalse(t1 is t2)
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

    def testQDateHash(self):
        d1 = QDate(1968, 3, 9)
        d2 = QDate(1968, 3, 9)
        self.assertFalse(d1 is d2)
        self.assertEqual(d1, d2)
        self.assertEqual(hash(d1), hash(d2))

    def testQDateTimeHash(self):
        d1 = QDateTime(QDate(1968, 3, 9), QTime(5, 5, 5))
        d2 = QDateTime(QDate(1968, 3, 9), QTime(5, 5, 5))
        self.assertFalse(d1 is d2)
        self.assertEqual(d1, d2)
        self.assertEqual(hash(d1), hash(d2))

    def testQUrlHash(self):
        u1 = QUrl(URL)
        u2 = QUrl(URL)
        self.assertFalse(u1 is u2)
        self.assertEqual(u1, u2)
        self.assertEqual(hash(u1), hash(u2))


if __name__ == '__main__':
    unittest.main()
