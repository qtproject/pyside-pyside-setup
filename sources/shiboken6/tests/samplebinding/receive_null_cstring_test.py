#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for a function that could receive a NULL pointer in a '[const] char*' parameter.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import countCharacters

class ReceiveNullCStringTest(unittest.TestCase):
    '''Test case for a function that could receive a NULL pointer in a '[const] char*' parameter.'''

    def testBasic(self):
        '''The test function should be working for the basic cases.'''
        a = ''
        b = 'abc'
        self.assertEqual(countCharacters(a), len(a))
        self.assertEqual(countCharacters(b), len(b))

    def testReceiveNull(self):
        '''The test function returns '-1' when receives a None value instead of a string.'''
        self.assertEqual(countCharacters(None), -1)

if __name__ == '__main__':
    unittest.main()

