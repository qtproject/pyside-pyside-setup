#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests user defined primitive type from a required module.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from other import Number

class UserDefinedPrimitiveTypeFromRequiredModuleTest(unittest.TestCase):

    def testUsersPrimitiveFromRequiredModuleAsArgument(self):
        '''static Number Number::fromComplex(Complex)'''
        cpx = complex(3.0, 1.2)
        number = Number.fromComplex(cpx)
        self.assertEqual(number.value(), int(cpx.real))

    def testUsersPrimitiveFromRequiredModuleAsReturnValue(self):
        '''Complex Number::toComplex()'''
        number = Number(12)
        cpx = number.toComplex()
        self.assertEqual(number.value(), int(cpx.real))

if __name__ == '__main__':
    unittest.main()
