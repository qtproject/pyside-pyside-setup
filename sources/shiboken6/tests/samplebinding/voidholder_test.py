#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for a class that holds a void pointer.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import VoidHolder, Point
from shiboken6 import Shiboken

class VoidHolderTest(unittest.TestCase):
    '''Test case for void pointer manipulation.'''

    def testGetVoidPointerFromCppAndPutsOnVoidHolder(self):
        '''Passes a void pointer created in C++ to be kept by VoidHolder.'''
        voidptr = VoidHolder.gimmeMeSomeVoidPointer()
        voidholder = VoidHolder(voidptr)
        self.assertEqual(voidptr, voidholder.voidPointer())

    def testPassVoidPointerAsArgument(self):
        '''Passes a void pointer created in C++ as an argument to a function.'''
        voidptr = VoidHolder.gimmeMeSomeVoidPointer()
        voidHolder = VoidHolder()
        returnValue = voidHolder.takeVoidPointer(voidptr)
        self.assertEqual(returnValue, voidptr)

    def testPutRandomObjectInsideVoidHolder(self):
        '''Passes a C++ pointer for an object created in Python to be kept by VoidHolder.'''
        obj = Point(1, 2)
        voidholder = VoidHolder(obj)
        self.assertEqual(Shiboken.getCppPointer(obj)[0], int(voidholder.voidPointer()))

    def testGetNoneObjectFromVoidHolder(self):
        '''A VoidHolder created without parameters returns a NULL pointer
           that should be converted to a Python None.'''
        voidholder = VoidHolder()
        self.assertEqual(voidholder.voidPointer(), None)

if __name__ == '__main__':
    unittest.main()

