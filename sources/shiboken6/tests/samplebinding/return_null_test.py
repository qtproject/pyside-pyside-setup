#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for functions that could return a NULL pointer.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import returnNullPrimitivePointer, returnNullValueTypePointer, returnNullObjectTypePointer

class ReturnNullTest(unittest.TestCase):
    '''Test case for functions that could return a NULL pointer.'''

    def testReturnNull(self):
        '''Function returns a NULL pointer to a primitive type.'''
        o = returnNullPrimitivePointer()
        self.assertEqual(o, None)

    def testReturnNullObjectType(self):
        '''Function returns a NULL pointer to an object-type.'''
        o = returnNullObjectTypePointer()
        self.assertEqual(o, None)

    def testReturnNullValueType(self):
        '''Function returns a NULL pointer to a value-type.'''
        o = returnNullValueTypePointer()
        self.assertEqual(o, None)

if __name__ == '__main__':
    unittest.main()

