#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QCollator'''

import ctypes
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCollator, QLocale, Qt


class QCollatorTest(unittest.TestCase):
    def testState(self):
        c = QCollator()
        c.setCaseSensitivity(Qt.CaseInsensitive)
        c.setLocale(QLocale.German)

        print("compare a and b:", c.compare("a", "b"))

        self.assertEqual(c.caseSensitivity(), Qt.CaseInsensitive)
        self.assertEqual(c.locale(), QLocale(QLocale.German))

        c.setLocale(QLocale.French)
        c.setNumericMode(True)
        c.setIgnorePunctuation(True)
        c.setLocale(QLocale.NorwegianBokmal)

        self.assertEqual(c.caseSensitivity(), Qt.CaseInsensitive)
        self.assertEqual(c.numericMode(), True)
        self.assertEqual(c.ignorePunctuation(), True)
        self.assertEqual(c.locale(), QLocale(QLocale.NorwegianBokmal))


if __name__ == '__main__':
    unittest.main()
