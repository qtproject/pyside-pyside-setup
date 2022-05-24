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

class MetaA(type):
    pass

class A(object):
    __metaclass__ = MetaA

MetaB = type(Point)
B = Point

class MetaC(MetaA, MetaB):
    pass
class C(A, B):
    __metaclass__ = MetaC

class D(C):
    pass

class TestMetaClass(unittest.TestCase):
    def testIt(self):
        w1 = C() # works
        w1.setX(1)
        w1.setY(2)

        w2 = D() # should work!
        w2.setX(3)
        w2.setY(4)

        w3 = w1 + w2
        self.assertEqual(w3.x(), 4)
        self.assertEqual(w3.y(), 6)
