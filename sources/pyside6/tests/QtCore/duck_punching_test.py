#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for duck punching new implementations of C++ virtual methods into object instances.'''

import gc
import os
import sys
import types
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from helper.usesqapplication import UsesQApplication


def MethodType(func, instance, instanceType):
    return types.MethodType(func, instance)


class Duck(QObject):
    def __init__(self):
        super().__init__()

    def childEvent(self, event):
        QObject.childEvent(self, event)


class TestDuckPunchingOnQObjectInstance(UsesQApplication):
    '''Test case for duck punching new implementations of C++ virtual methods into object instances.'''

    def setUp(self):
        # Acquire resources
        self.duck_childEvent_called = False
        UsesQApplication.setUp(self)

    def tearDown(self):
        # Release resources
        del self.duck_childEvent_called
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        UsesQApplication.tearDown(self)

    def testChildEventMonkeyPatch(self):
        # Test if the new childEvent injected on QObject instance is called from C++
        parent = QObject()

        def childEvent(obj, event):
            self.duck_childEvent_called = True
        parent.childEvent = MethodType(childEvent, parent, QObject)
        child = QObject()
        child.setParent(parent)
        self.assertTrue(self.duck_childEvent_called)
        # This is done to decrease the refcount of the vm object
        # allowing the object wrapper to be deleted before the
        # BindingManager. This is useful when compiling Shiboken
        # for debug, since the BindingManager destructor has an
        # assert that checks if the wrapper mapper is empty.
        parent.childEvent = None

    def testChildEventMonkeyPatchWithInheritance(self):
        # Test if the new childEvent injected on a QObject's extension class instance is called from C++
        parent = Duck()

        def childEvent(obj, event):
            QObject.childEvent(obj, event)
            self.duck_childEvent_called = True
        child = QObject()
        child.setParent(parent)
        parent.childEvent = MethodType(childEvent, parent, QObject)
        child = QObject()
        child.setParent(parent)
        self.assertTrue(self.duck_childEvent_called)
        # This is done to decrease the refcount of the vm object
        # allowing the object wrapper to be deleted before the
        # BindingManager. This is useful when compiling Shiboken
        # for debug, since the BindingManager destructor has an
        # assert that checks if the wrapper mapper is empty.
        parent.childEvent = None


if __name__ == '__main__':
    unittest.main()

