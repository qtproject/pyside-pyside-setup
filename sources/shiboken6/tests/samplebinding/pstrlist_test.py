#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
import sample

class PStrListTest(unittest.TestCase):

    def testPStrList(self):
        a = 'str0'
        b = 'str1'
        lst = sample.createPStrList(a, b)
        self.assertEqual(lst, [a, b])

    def testListOfPStr(self):
        a = 'str0'
        b = 'str1'
        lst = sample.createListOfPStr(a, b)
        self.assertEqual(lst, [a, b])

if __name__ == '__main__':
    unittest.main()
