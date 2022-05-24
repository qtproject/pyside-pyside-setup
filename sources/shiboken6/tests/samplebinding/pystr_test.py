#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for definition of __str__ method.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Point

class PyStrTest(unittest.TestCase):
    '''Test case for definition of __str__ method.'''

    def testPyStr(self):
        '''Test case for defined __str__ method.'''
        pt = Point(5, 2)
        self.assertEqual(str(pt), 'Point(5.0, 2.0)')

if __name__ == '__main__':
    unittest.main()

