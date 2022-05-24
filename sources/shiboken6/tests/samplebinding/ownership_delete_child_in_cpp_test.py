#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for destroy a child object in C++'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType


class DeleteChildInCpp(unittest.TestCase):
    '''Test case for destroying a child in c++'''

    def testDeleteChild(self):
        '''Delete child in C++ should invalidate child - using C++ wrapper'''
        parent = ObjectType()
        parent.setObjectName('parent')
        child = ObjectType(parent)
        child.setObjectName('child')

        parent.killChild('child')
        self.assertRaises(RuntimeError, child.objectName)
        self.assertEqual(parent.objectName(), 'parent')

if __name__ == '__main__':
    unittest.main()
