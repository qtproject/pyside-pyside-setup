#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for implicit conversions'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ImplicitConv, ObjectType

class ImplicitConvTest(unittest.TestCase):
    '''Test case for implicit conversions'''

    def testImplicitConversions(self):
        '''Test if overloaded function call decisor takes implicit conversions into account.'''
        ic = ImplicitConv.implicitConvCommon(ImplicitConv())
        self.assertEqual(ic.ctorEnum(), ImplicitConv.CtorNone)

        ic = ImplicitConv.implicitConvCommon(3)
        self.assertEqual(ic.ctorEnum(), ImplicitConv.CtorOne)
        self.assertEqual(ic.objId(), 3)

        ic = ImplicitConv.implicitConvCommon(ImplicitConv.CtorThree)
        self.assertEqual(ic.ctorEnum(), ImplicitConv.CtorThree)

        obj = ObjectType()
        ic = ImplicitConv.implicitConvCommon(obj)
        self.assertEqual(ic.ctorEnum(), ImplicitConv.CtorObjectTypeReference)

        ic = ImplicitConv.implicitConvCommon(42.42)
        self.assertEqual(ic.value(), 42.42)

        ic = ImplicitConv(None)
        self.assertEqual(ic.ctorEnum(), ImplicitConv.CtorPrimitiveType)


if __name__ == '__main__':
    unittest.main()

