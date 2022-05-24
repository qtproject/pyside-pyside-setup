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

from sample import Overload, Str


class OverloadTest(unittest.TestCase):

    def testNoArgument(self):
        overload = Overload()
        self.assertEqual(overload.strBufferOverloads(), Overload.Function2)

    def testStrArgument(self):
        overload = Overload()
        self.assertEqual(overload.strBufferOverloads(Str('')), Overload.Function0)
        self.assertEqual(overload.strBufferOverloads(Str(''), ''), Overload.Function0)
        self.assertEqual(overload.strBufferOverloads(Str(''), '', False), Overload.Function0)

    def testStringArgumentAsStr(self):
        overload = Overload()
        self.assertEqual(overload.strBufferOverloads('', ''), Overload.Function0)
        self.assertEqual(overload.strBufferOverloads('', '', False), Overload.Function0)

    def testStringArgumentAsBuffer(self):
        overload = Overload()
        self.assertEqual(overload.strBufferOverloads(bytes('', "UTF-8"), 0), Overload.Function1)

    def testBufferArgument(self):
        overload = Overload()
        self.assertEqual(overload.strBufferOverloads(bytes('', "UTF-8"), 0), Overload.Function1)

if __name__ == '__main__':
    unittest.main()

