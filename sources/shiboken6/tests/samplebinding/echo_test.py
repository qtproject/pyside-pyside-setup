#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for <add-function> with const char* as argument'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Echo

class TestEcho(unittest.TestCase):
    '''Simple test case for Echo.echo'''

    def testEcho(self):
        '''Test function added with const char * as arg'''
        x = 'Foobar'
        y = Echo().echo(x)
        self.assertEqual(x, y)

    def testCallOperator(self):
        e = Echo()
        self.assertEqual(e("Hello", 3), "Hello3");
if __name__ == '__main__':
    unittest.main()

