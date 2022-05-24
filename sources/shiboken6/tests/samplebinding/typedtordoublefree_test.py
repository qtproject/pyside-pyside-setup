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
from sample import ObjectType

class TestTypeDestructorDoubleFree(unittest.TestCase):
    def testTypeDestructorDoubleFree(self):
        '''Causes the type destructors of two derived classes to be called.'''
        def scope():
            class ExtObj1(ObjectType):
                def __init__(self):
                    ObjectType.__init__(self)
            obj = ExtObj1()
            child = ObjectType(parent=obj)
            self.assertEqual(obj.takeChild(child), child)
            class ExtObj2(ObjectType):
                def __init__(self):
                    ObjectType.__init__(self)
            obj = ExtObj2()
            child = ObjectType(parent=obj)
            self.assertEqual(obj.takeChild(child), child)
        scope()

if __name__ == '__main__':
    unittest.main()
