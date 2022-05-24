#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for the SmartPtrTester class'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from smart import Integer
from sample import Str
from other import SmartPtrTester


class SmartPtrTest(unittest.TestCase):
    '''Test case for the SmartPtrTester class'''

    def test(self):
        tester = SmartPtrTester()

        integerPtr = tester.createSharedPtrInteger(42)
        self.assertEqual(tester.valueOfSharedPtrInteger(integerPtr), 42)

        strPtr = tester.createSharedPtrStr('hello')
        self.assertEqual(tester.valueOfSharedPtrStr(strPtr), 'hello')


if __name__ == '__main__':
    unittest.main()
