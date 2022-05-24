#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for proper generation of constructor altered by conversion-rule tag.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import CtorConvRule

class TestCtorConvRule(unittest.TestCase):
    '''Simple test case for CtorConvRule'''

    def testCtorConvRule(self):
        '''Test CtorConvRule argument modification through conversion-rule tag.'''
        value = 123
        obj = CtorConvRule(value)
        self.assertEqual(obj.value(), value + 1)

if __name__ == '__main__':
    unittest.main()

