# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import datetime
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QDateTime, QDate, QTime


class TestQDate (unittest.TestCase):
    def testDateConversion(self):
        dateTime = QDateTime(QDate(2011, 5, 17), QTime(11, 1, 14, 15))
        dateTimePy = QDateTime(datetime.date(2011, 5, 17), datetime.time(11, 1, 14, 15000))
        self.assertEqual(dateTime, dateTimePy)

    def testDateTimeConversion(self):
        dateTime = QDateTime(QDate(2011, 5, 17), QTime(11, 1, 14, 15))
        dateTimePy = QDateTime(datetime.datetime(2011, 5, 17, 11, 1, 14, 15000))
        self.assertEqual(dateTime, dateTimePy)

    def testDateTimeNow(self):
        py = datetime.datetime.now()
        qt = QDateTime(py)
        self.assertEqual(qt, py)


if __name__ == '__main__':
    unittest.main()
