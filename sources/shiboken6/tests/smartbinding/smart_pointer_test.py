#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from copy import copy
from smart import Obj, Registry, Integer


def objCount():
    return Registry.getInstance().countObjects()


def integerCount():
    return Registry.getInstance().countIntegers()


class SmartPointerTests(unittest.TestCase):

    def setUp(self):
        super().setUp()
        if os.environ.get("VERBOSE"):
            Registry.getInstance().setVerbose(True)

    def testObjSmartPointer(self):
        # Create Obj.
        o = Obj()
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 1)

        # Create a shared pointer to an Obj together with an Obj.
        ptrToObj = o.createSharedPtrObj()
        self.assertEqual(objCount(), 2)

        # Delete the old Obj.
        o = None
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 1)

        # Get a wrapper to the Obj inside of the shared pointer, object count
        # should not change.
        obj = ptrToObj.data()
        self.assertEqual(objCount(), 1)
        obj.m_integer = 50
        self.assertEqual(obj.m_integer, 50)

        # Set and get a member value via shared pointer (like operator->).
        ptrToObj.m_integer = 100
        self.assertEqual(ptrToObj.m_integer, 100)

        # Get inner PyObject via shared pointer (like operator->) and set
        # value in it.
        ptrToObj.m_internalInteger.m_int = 200
        self.assertEqual(ptrToObj.m_internalInteger.m_int, 200)

        # Pass smart pointer as argument to a method, return value is the value
        # of m_integer of passed Obj inside the smart pointer.
        result = ptrToObj.takeSharedPtrToObj(ptrToObj)
        self.assertEqual(result, 100)

        # Pass an Integer as an argument that returns itself.
        result = ptrToObj.takeInteger(ptrToObj.m_internalInteger)
        self.assertEqual(integerCount(), 2)
        result = None
        if integerCount() > 1:
            gc.collect()
            print('Running garbage collector for reference test',
                  file=sys.stderr)
        self.assertEqual(integerCount(), 1)

        # Make a copy of the shared pointer, object count should not change.
        ptrToObj2 = copy(ptrToObj)
        self.assertEqual(objCount(), 1)

        # Delete the first shared pointer, object count should not change
        # because the second one still has a reference.
        del ptrToObj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 1)

        # Delete the second smart pointer, object should be deleted.
        del ptrToObj2
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 0)
        self.assertEqual(integerCount(), 0)

    def testIntegerSmartPointer(self):
        # Create Obj.
        o = Obj()
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 1)

        # Create a shared pointer to an Integer together with an Integer.
        ptrToInteger = o.createSharedPtrInteger()
        self.assertEqual(objCount(), 1)
        self.assertEqual(integerCount(), 2)

        # Get a wrapper to the Integer inside of the shared pointer, integer
        # count should not change.
        integer = ptrToInteger.data()
        self.assertEqual(integerCount(), 2)
        integer.m_int = 50
        self.assertEqual(integer.m_int, 50)

        # Set and get a member value via shared pointer (like operator->).
        ptrToInteger.setValue(150)
        self.assertEqual(ptrToInteger.value(), 150)

        # Set and get a member field via shared pointer (like operator->).
        ptrToInteger.m_int = 100
        self.assertEqual(ptrToInteger.m_int, 100)

        # Pass smart pointer as argument to a method, return value is the
        # value of m_int of passed Integer inside the smart pointer.
        result = o.takeSharedPtrToInteger(ptrToInteger)
        self.assertEqual(result, 100)

        # Make a copy of the shared pointer, integer count should not change.
        ptrToInteger2 = copy(ptrToInteger)
        self.assertEqual(integerCount(), 2)

        # Delete the first shared pointer, integer count should not change
        # because the second one still has a reference.
        del ptrToInteger
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(integerCount(), 2)

        # Delete the second smart pointer, integer should be deleted.
        del ptrToInteger2
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 1)
        self.assertEqual(integerCount(), 1)

        # Delete the original object which was used to create the integer.
        del o
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 0)
        self.assertEqual(integerCount(), 0)

    def testConstIntegerSmartPointer(self):
        # Create Obj.
        o = Obj()
        ptrToConstInteger = o.createSharedPtrConstInteger()
        self.assertEqual(ptrToConstInteger.m_int, 456)
        result = o.takeSharedPtrToConstInteger(ptrToConstInteger)
        self.assertEqual(result, 456)
        self.assertEqual(ptrToConstInteger.value(), 456)

    def testSmartPointersWithNamespace(self):
        # Create the main object
        o = Obj()
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 1)

        # Create a shared pointer to an Integer together with an Integer.
        ptrToInteger = o.createSharedPtrInteger2()
        self.assertEqual(objCount(), 1)
        self.assertEqual(integerCount(), 2)

        integer = ptrToInteger.data()
        self.assertTrue(integer)

    def testListOfSmartPointers(self):
        # Create the main object
        o = Obj()

        # Create a list of shared objects
        ptrToObjList = o.createSharedPtrObjList(10)
        self.assertEqual(len(ptrToObjList), 10)
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 11)

        # Remove one from the list
        ptrToObjList.pop()
        self.assertEqual(len(ptrToObjList), 9)
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertEqual(objCount(), 10)

        # clear and delete all objects in the list
        del ptrToObjList[:]  # Python 2.7 lists have no clear method
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(len(ptrToObjList), 0)
        self.assertEqual(objCount(), 1)

    def testInvalidParameter(self):
        # Create Obj.
        o = Obj()
        # Create a shared pointer to an Obj together with an Obj.
        ptrToObj = o.createSharedPtrObj()
        try:
            ptrToObj.typo
            self.assertFail()
        except AttributeError as error:
            self.assertEqual(error.args[0], "'smart.SharedPtr_Obj' object has no attribute 'typo'")

    def testSmartPointerConversions(self):
        # Create Obj.
        o = Obj()
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertEqual(objCount(), 1)
        self.assertEqual(integerCount(), 1)

        # Create a shared pointer to an Integer2
        integer2 = o.createSharedPtrInteger2()
        self.assertEqual(integer2.value(), 456)

        # pass Smart<Integer2> to a function that accepts Smart<Integer>
        r = o.takeSharedPtrToInteger(integer2)
        self.assertEqual(r, integer2.value())

    def testSmartPointerValueComparison(self):
        """Test a pointee class with comparison operators."""
        four = Obj.createSharedPtrInteger(4)
        four2 = Obj.createSharedPtrInteger(4)
        five = Obj.createSharedPtrInteger(5)
        self.assertTrue(four == four)
        self.assertTrue(four == four2)
        self.assertFalse(four != four)
        self.assertFalse(four != four2)
        self.assertFalse(four < four)
        self.assertTrue(four <= four)
        self.assertFalse(four > four)
        self.assertTrue(four >= four)
        self.assertFalse(four == five)
        self.assertTrue(four != five)
        self.assertTrue(four < five)
        self.assertTrue(four <= five)
        self.assertFalse(four > five)
        self.assertFalse(four >= five)
        self.assertTrue(five > four)

        self.assertRaises(NotImplementedError,
                          lambda : Obj.createNullSharedPtrInteger() == four)

    def testSmartPointerObjectComparison(self):
        """Test a pointee class without comparison operators."""
        o1 = Obj.createSharedPtrObj()
        o2 = Obj.createSharedPtrObj()
        self.assertTrue(o1 == o1)
        self.assertFalse(o1 != o1)
        self.assertFalse(o1 == o2)
        self.assertTrue(o1 != o2)

    def testOperatorNbBool(self):
        null_ptr = Obj.createNullSharedPtrInteger()
        self.assertFalse(null_ptr)
        zero = Obj.createSharedPtrInteger(0)
        self.assertTrue(zero)

    def testParameterNone(self):
        o = Obj()
        null_ptr = Obj.createNullSharedPtrInteger()
        o.takeSharedPtrToInteger(null_ptr)
        o.takeSharedPtrToIntegerByConstRef(null_ptr)
        o.takeSharedPtrToInteger(None)
        o.takeSharedPtrToIntegerByConstRef(None)


if __name__ == '__main__':
    unittest.main()
