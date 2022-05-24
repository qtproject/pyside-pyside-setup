#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for __hash__'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *

class HashableTest(unittest.TestCase):

    def testStrHash(self):
        h = {}
        s = Str("Hi")
        h[s] = 2
        self.assertTrue(h.get(s), 2)

    def testObjectTypeHash(self):
        h = {}
        o = ObjectType()
        h[o] = 2
        self.assertTrue(h.get(o), 2)

if __name__ == '__main__':
    unittest.main()

