#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests calling NoImplicitConversion using a ExtendsNoImplicitConversion parameter,
   being that the latter defines a new conversion operator for the former, and this one
   has no implicit conversions.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import NoImplicitConversion
from other import ExtendsNoImplicitConversion

class ConversionOperatorForClassWithoutImplicitConversionsTest(unittest.TestCase):
    '''Tests calling NoImplicitConversion constructor using a ExtendsNoImplicitConversion parameter.'''

    def testNoImplicitConversion(self):
        '''Basic test to see if the NoImplicitConversion is Ok.'''
        obj = NoImplicitConversion(123)
        # NoImplicitConversion.receivesNoImplicitConversionByValue(NoImplicitConversion)
        self.assertEqual(obj.objId(), NoImplicitConversion.receivesNoImplicitConversionByValue(obj))
        # NoImplicitConversion.receivesNoImplicitConversionByPointer(NoImplicitConversion*)
        self.assertEqual(obj.objId(), NoImplicitConversion.receivesNoImplicitConversionByPointer(obj))
        # NoImplicitConversion.receivesNoImplicitConversionByReference(NoImplicitConversion&)
        self.assertEqual(obj.objId(), NoImplicitConversion.receivesNoImplicitConversionByReference(obj))

    def testPassingExtendsNoImplicitConversionAsNoImplicitConversionByValue(self):
        '''Gives an ExtendsNoImplicitConversion object to a function expecting a NoImplicitConversion, passing by value.'''
        obj = ExtendsNoImplicitConversion(123)
        self.assertEqual(obj.objId(), NoImplicitConversion.receivesNoImplicitConversionByValue(obj))

    def testPassingExtendsNoImplicitConversionAsNoImplicitConversionByReference(self):
        '''Gives an ExtendsNoImplicitConversion object to a function expecting a NoImplicitConversion, passing by reference.'''
        obj = ExtendsNoImplicitConversion(123)
        self.assertEqual(obj.objId(), NoImplicitConversion.receivesNoImplicitConversionByReference(obj))

    def testPassingExtendsNoImplicitConversionAsNoImplicitConversionByPointer(self):
        '''Gives an ExtendsNoImplicitConversion object to a function expecting a NoImplicitConversion, passing by pointer.
           This should not be accepted, since pointers should not be converted.'''
        obj = ExtendsNoImplicitConversion(123)
        self.assertRaises(TypeError, NoImplicitConversion.receivesNoImplicitConversionByPointer, obj)


if __name__ == '__main__':
    unittest.main()

