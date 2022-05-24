#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for ...'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType

class DerivedObjectType(ObjectType):
    def isPython(self):
        return True

    def createChild(self, parent):
        return DerivedObjectType(parent)

class ParentTest(unittest.TestCase):

    def testUunsafeParent(self):
        o = DerivedObjectType()
        o.callVirtualCreateChild()

if __name__ == '__main__':
    unittest.main()

