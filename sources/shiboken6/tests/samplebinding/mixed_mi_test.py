#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for multiple inheritance in mixed Python/C++ scenarios'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType


class Base(object):
    '''Base Python class'''

    def __init__(self):
        self.name = ''

    def pythonName(self):
        return self.name

    def setPythonName(self, name):
        self.name = name


class Child(Base, ObjectType):
    '''Dummy class with mixed parents'''

    def __init__(self):
        Base.__init__(self)
        ObjectType.__init__(self)


class MixedInheritanceTest(unittest.TestCase):

    def testMixed(self):
        '''Mixed Python/C++ multiple inheritance'''
        obj = Child()

        obj.setObjectName('aaa')
        self.assertEqual(obj.objectName(), 'aaa')

        obj.setPythonName('python')
        self.assertEqual(obj.pythonName(), 'python')


if __name__ == '__main__':
    unittest.main()


