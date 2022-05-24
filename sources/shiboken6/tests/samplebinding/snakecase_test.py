#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for snake case generation'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import (SnakeCaseTest, SnakeCaseDerivedTest,
                    snake_case_global_function)


class OverrideTest(SnakeCaseDerivedTest):
    def virtual_func(self):
        return 4711


class SnakeCaseTestCase(unittest.TestCase):
    '''Test for SnakeCaseTest'''
    def testMemberFunctions(self):
        s = SnakeCaseTest()
        self.assertEqual(s.test_function1(), 42)

        self.assertEqual(s.testFunctionDisabled(), 42)

        self.assertEqual(s.testFunctionBoth(), 42)
        self.assertEqual(s.test_function_both(), 42)

    def virtualFunctions(self):
        s = OverrideTest()
        self.assertEqual(s.call_virtual_func(), 4711)

    def testMemberFields(self):
        s = SnakeCaseTest()
        old_value = s.test_field
        s.test_field = old_value + 1
        self.assertEqual(s.test_field, old_value + 1)

        old_value = s.testFieldDisabled
        s.testFieldDisabled = old_value + 1
        self.assertEqual(s.testFieldDisabled, old_value + 1)

        old_value = s.test_field_both
        s.test_field_both = old_value + 1
        self.assertEqual(s.test_field_both, old_value + 1)
        self.assertEqual(s.testFieldBoth, old_value + 1)

    def testGlobalFunction(self):
        self.assertEqual(snake_case_global_function(), 42)


if __name__ == '__main__':
    unittest.main()
