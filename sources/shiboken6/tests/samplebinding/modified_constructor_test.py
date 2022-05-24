#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests cases for ConstructorWithModifiedArgument class.'''

import sys
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *


class ConstructorWithModifiedArgumentTest(unittest.TestCase):
    '''Test cases for ConstructorWithModifiedArgument class.'''

    def testConstructorWithModifiedArgument(self):
        sampleClass = ModifiedConstructor("10")
        self.assertTrue(sampleClass.retrieveValue(), 10)

if __name__ == '__main__':
    unittest.main()

