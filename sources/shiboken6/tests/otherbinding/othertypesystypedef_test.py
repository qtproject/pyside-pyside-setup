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

from other import (OtherValueWithUnitUser, ValueWithUnitIntInch,
                   ValueWithUnitIntMillimeter)
from sample import (ValueWithUnitDoubleMillimeter)


class OtherTypeSysTypeDefTest(unittest.TestCase):
    '''Test case type system typedefs across modules.'''

    def test(self):
        # Exercise existing typedefs from "sample"
        mm_value = ValueWithUnitDoubleMillimeter(2540)
        inch_value = OtherValueWithUnitUser.doubleMillimeterToInch(mm_value)
        self.assertEqual(int(inch_value.value()), 10)
        # Exercise typedefs in "other"
        mm_value = ValueWithUnitIntMillimeter(2540)
        inch_value = OtherValueWithUnitUser.intMillimeterToInch(mm_value)
        self.assertEqual(inch_value.value(), 10)


if __name__ == '__main__':
    unittest.main()
