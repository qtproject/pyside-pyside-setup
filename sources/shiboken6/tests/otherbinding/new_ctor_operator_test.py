#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests calling Str constructor using a Number parameter, being that number defines a cast operator to Str.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Str
from other import Number

class NewCtorOperatorTest(unittest.TestCase):
    '''Tests calling Str constructor using a Number parameter, being that number defines a cast operator to Str.'''

    def testNumber(self):
        '''Basic test to see if the Number class is Ok.'''
        value = 123
        num = Number(value)
        self.assertEqual(num.value(), value)

    def testStrCtorWithNumberArgument(self):
        '''Try to build a Str from 'sample' module with a Number argument from 'other' module.'''
        value = 123
        num = Number(value)
        string = Str(num)

if __name__ == '__main__':
    unittest.main()

