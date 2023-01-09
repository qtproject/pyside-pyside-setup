#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QLocale'''

import ctypes
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QLocale


class QLocaleTestToNumber(unittest.TestCase):
    def testToNumberInt(self):
        obj = QLocale(QLocale.C)
        self.assertEqual((37, True), obj.toInt('37'))

    def testToNumberFloat(self):
        obj = QLocale(QLocale.C)
        self.assertEqual((ctypes.c_float(37.109).value, True),
                         obj.toFloat('37.109'))

    def testToNumberDouble(self):
        obj = QLocale(QLocale.C)
        self.assertEqual((ctypes.c_double(37.109).value, True),
                         obj.toDouble('37.109'))

    def testToNumberShort(self):
        obj = QLocale(QLocale.C)
        self.assertEqual((ctypes.c_short(37).value, True),
                         obj.toShort('37'))

    def testToNumberULongLong(self):
        obj = QLocale(QLocale.C)
        self.assertEqual((ctypes.c_ulonglong(37).value, True),
                         obj.toULongLong('37'))

    def testToNumberULongLongNegative(self):
        obj = QLocale(QLocale.C)
        self.assertTrue(not obj.toULongLong('-37')[1])

    def testToCurrencyString(self):
        """PYSIDE-2133, do not use int overload, dropping decimals."""
        en_locale = QLocale("en_US")
        value = en_locale.toCurrencyString(1234.56)
        self.assertEqual(value, "$1,234.56")

    def testToString(self):
        """PYSIDE-2168, check negative values"""
        en_locale = QLocale("en_US")
        value = en_locale.toString(-4)
        self.assertEqual(value, "-4")
        # Verify that large types (long long/double) are used.
        value = en_locale.toString(3000000000)
        self.assertEqual(value, "3,000,000,000")
        value = en_locale.toString(10e40)
        self.assertEqual(value, "1E+41")


if __name__ == '__main__':
    unittest.main()
