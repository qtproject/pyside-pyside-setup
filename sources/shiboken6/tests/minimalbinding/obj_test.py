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
from minimal import Obj

class ExtObj(Obj):
    def __init__(self, objId):
        Obj.__init__(self, objId)
        self.virtual_method_called = False

    def virtualMethod(self, val):
        self.virtual_method_called = True
        return not Obj.virtualMethod(self, val)

    def passObjectType(self, obj):
        obj.setObjId(obj.objId() + 1)
        return obj

    def passObjectTypeReference(self, obj):
        obj.setObjId(obj.objId() + 1)
        return obj


class ObjTest(unittest.TestCase):

    def testNormalMethod(self):
        objId = 123
        obj = Obj(objId)
        self.assertEqual(obj.objId(), objId)

    def testNormalMethodFromExtendedClass(self):
        objId = 123
        obj = ExtObj(objId)
        self.assertEqual(obj.objId(), objId)

    def testVirtualMethod(self):
        obj = Obj(0)
        even_number = 8
        self.assertEqual(obj.virtualMethod(even_number), obj.callVirtualMethod(even_number))

    def testVirtualMethodFromExtendedClass(self):
        obj = ExtObj(0)
        even_number = 8
        self.assertEqual(obj.virtualMethod(even_number), obj.callVirtualMethod(even_number))
        self.assertTrue(obj.virtual_method_called)

    def testPassObjectType(self):
        obj = Obj(0)
        self.assertEqual(obj, obj.passObjectType(obj))
        self.assertEqual(obj, obj.callPassObjectType(obj))

    def testPassObjectTypeNone(self):
        obj = Obj(0)
        self.assertEqual(None, obj.passObjectType(None))
        self.assertEqual(None, obj.callPassObjectType(None))

    def testPassObjectTypeReference(self):
        obj = Obj(0)
        self.assertEqual(obj, obj.passObjectTypeReference(obj))
        self.assertEqual(obj, obj.callPassObjectTypeReference(obj))

    def testPassObjectTypeFromExtendedClass(self):
        obj = ExtObj(0)
        self.assertEqual(obj.objId(), 0)
        sameObj = obj.passObjectType(obj)
        self.assertEqual(obj, sameObj)
        self.assertEqual(sameObj.objId(), 1)
        sameObj = obj.callPassObjectType(obj)
        self.assertEqual(obj, sameObj)
        self.assertEqual(sameObj.objId(), 2)

    def testPassObjectTypeReferenceFromExtendedClass(self):
        obj = ExtObj(0)
        self.assertEqual(obj.objId(), 0)
        sameObj = obj.passObjectTypeReference(obj)
        self.assertEqual(obj, sameObj)
        self.assertEqual(sameObj.objId(), 1)
        sameObj = obj.callPassObjectTypeReference(obj)
        self.assertEqual(obj, sameObj)
        self.assertEqual(sameObj.objId(), 2)


if __name__ == '__main__':
    unittest.main()

