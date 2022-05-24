#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for finding scope in cases involving inheritance.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import SampleNamespace

class ScopeAndInheritanceTest(unittest.TestCase):
    '''Test cases for finding scope in cases involving inheritance.'''

    def testMethodCorrectlyWrapper(self):
        '''A method returning a type declared in the scope of the method's
        class parent must be found and the method correctly exported.'''
        meth = getattr(SampleNamespace.DerivedFromNamespace, 'methodReturningTypeFromParentScope')

if __name__ == '__main__':
    unittest.main()

