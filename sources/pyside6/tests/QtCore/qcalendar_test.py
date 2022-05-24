#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QCalendar (5.14)'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCalendar


class TestQCalendar (unittest.TestCase):
    def testCalendar(self):
        calendar = QCalendar(QCalendar.System.Gregorian)
        self.assertTrue(calendar.isGregorian())
        self.assertEqual(calendar.name(), 'Gregorian')
        self.assertFalse(calendar.hasYearZero())
        self.assertEqual(calendar.monthsInYear(2019), 12)


if __name__ == '__main__':
    unittest.main()
