#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for object reparenting.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
import sys

from sample import ObjectType

class ExtObjectType(ObjectType):
    def __init__(self):
        ObjectType.__init__(self)


class ReparentingTest(unittest.TestCase):
    '''Tests for object reparenting.'''

    def testReparentedObjectTypeIdentity(self):
        '''Reparent children from one parent to another.'''
        object_list = []
        old_parent = ObjectType()
        new_parent = ObjectType()
        for i in range(3):
            obj = ObjectType()
            object_list.append(obj)
            obj.setParent(old_parent)
        for obj in object_list:
            obj.setParent(new_parent)
        for child in new_parent.children():
            self.assertTrue(child in object_list)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReparentWithTheSameParent(self):
        '''Set the same parent twice to check if the ref continue the same'''
        obj = ObjectType()
        parent = ObjectType()
        self.assertEqual(sys.getrefcount(obj), 2)
        obj.setParent(parent)
        self.assertEqual(sys.getrefcount(obj), 3)
        obj.setParent(parent)
        self.assertEqual(sys.getrefcount(obj), 3)

    def testReparentedExtObjectType(self):
        '''Reparent children from one extended parent to another.'''
        object_list = []
        old_parent = ExtObjectType()
        new_parent = ExtObjectType()
        for i in range(3):
            obj = ExtObjectType()
            object_list.append(obj)
            obj.setParent(old_parent)
        for obj in object_list:
            obj.setParent(new_parent)
        for orig, child in zip(object_list, new_parent.children()):
            self.assertEqual(type(orig), type(child))

    def testReparentedObjectTypeIdentityWithParentsCreatedInCpp(self):
        '''Reparent children from one parent to another, both created in C++.'''
        object_list = []
        old_parent = ObjectType.create()
        new_parent = ObjectType.create()
        for i in range(3):
            obj = ObjectType()
            object_list.append(obj)
            obj.setParent(old_parent)
        for obj in object_list:
            obj.setParent(new_parent)
        for child in new_parent.children():
            self.assertTrue(child in object_list)

    def testReparentedObjectTypeIdentityWithChildrenCreatedInCpp(self):
        '''Reparent children created in C++ from one parent to another.'''
        object_list = []
        old_parent = ObjectType()
        new_parent = ObjectType()
        for i in range(3):
            obj = ObjectType.create()
            object_list.append(obj)
            obj.setParent(old_parent)
        for obj in object_list:
            obj.setParent(new_parent)
        for child in new_parent.children():
            self.assertTrue(child in object_list)

    def testReparentedObjectTypeIdentityWithParentsAndChildrenCreatedInCpp(self):
        '''Reparent children from one parent to another. Parents and children are created in C++.'''
        object_list = []
        old_parent = ObjectType.create()
        new_parent = ObjectType.create()
        for i in range(3):
            obj = ObjectType.create()
            object_list.append(obj)
            obj.setParent(old_parent)
        for obj in object_list:
            obj.setParent(new_parent)
        for child in new_parent.children():
            self.assertTrue(child in object_list)


if __name__ == '__main__':
    unittest.main()

