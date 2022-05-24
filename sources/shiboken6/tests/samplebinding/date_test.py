#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for python conversions types '''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from datetime import date

from sample import SbkDate

class DateConversionTest(unittest.TestCase):

    def testConstructorWithDateObject(self):
        pyDate = date(2010, 12, 12)
        cDate = SbkDate(pyDate)
        self.assertTrue(cDate.day(), pyDate.day)
        self.assertTrue(cDate.month(), pyDate.month)
        self.assertTrue(cDate.year(), pyDate.year)

    def testToPythonFunction(self):
        cDate = SbkDate(2010, 12, 12)
        pyDate = cDate.toPython()
        self.assertTrue(cDate.day(), pyDate.day)
        self.assertTrue(cDate.month(), pyDate.month)
        self.assertTrue(cDate.year(), pyDate.year)

if __name__ == '__main__':
    unittest.main()

