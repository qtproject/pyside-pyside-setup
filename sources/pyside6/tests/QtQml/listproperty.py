# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from PySide6.QtQml import ListProperty


class InheritsQObject(QObject):
    pass


def dummyFunc():
    pass


class TestListProperty(unittest.TestCase):
    def testIt(self):

        # Verify that type checking works properly
        type_check_error = False

        try:
            ListProperty(QObject)
            ListProperty(InheritsQObject)
        except:
            type_check_error = True

        self.assertFalse(type_check_error)

        try:
            ListProperty(int)
        except TypeError:
            type_check_error = True

        self.assertTrue(type_check_error)

        # Verify that method validation works properly
        method_check_error = False

        try:
            ListProperty(QObject, append=None, at=None, count=None, replace=None, clear=None, removeLast=None)  # Explicitly setting None
            ListProperty(QObject, append=dummyFunc)
            ListProperty(QObject, count=dummyFunc, at=dummyFunc)
        except:
            method_check_error = True

        self.assertFalse(method_check_error)

        try:
            ListPropery(QObject, append=QObject())
        except:
            method_check_error = True

        self.assertTrue(method_check_error)


if __name__ == '__main__':
    unittest.main()
