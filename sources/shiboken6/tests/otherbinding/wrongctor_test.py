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
from sample import *
from other import *

class Foo(OtherDerived):
    def __init__(self):
        Abstract.__init__(self, 2) # this should raise an exception

class Foo2(ObjectType, OtherDerived):
    def __init__(self):
        ObjectType.__init__(self)
        Abstract.__init__(self, 2) # this should raise an exception


class WrongCtorTest(unittest.TestCase):
    def testIt(self):
        self.assertRaises(TypeError, Foo)
        self.assertRaises(TypeError, Foo2)


if __name__ == '__main__':
    unittest.main()
