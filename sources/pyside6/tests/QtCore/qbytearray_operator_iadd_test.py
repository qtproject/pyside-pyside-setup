# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray
from helper.docmodifier import DocModifier


class BaseQByteArrayOperatorIAdd(object):
    '''Base class for QByteArray += operator tests.

    Implementing classes should inherit from unittest.TestCase and implement
    setUp, setting self.obj and self.orig_obj to the target QByteArray and original
    one, respectively'''

    __metaclass__ = DocModifier

    def testSingleString(self):
        '''QByteArray += bytes of size 1'''
        s = bytes('0', "UTF-8")
        self.obj += s
        self.assertEqual(self.obj, self.orig_obj + s)
        self.assertEqual(self.obj.size(), self.orig_obj.size() + len(s))

    def testString(self):
        '''QByteArray += bytes of size > 1'''
        s = bytearray(bytes('dummy', "UTF-8"))
        self.obj += s  # XXx iadd support abytearray
        self.assertEqual(self.obj, self.orig_obj + s)
        self.assertEqual(self.obj.size(), self.orig_obj.size() + len(s))

    def testQByteArray(self):
        '''QByteArray += QByteArray'''
        s = QByteArray(bytes('array', "UTF-8"))
        self.obj += s
        self.assertEqual(self.obj, self.orig_obj + s)


class NullQByteArrayOperatorIAdd(unittest.TestCase, BaseQByteArrayOperatorIAdd):
    '''Test case for operator QByteArray += on null QByteArrays'''

    doc_prefix = 'Null object'
    doc_filter = lambda x: x.startswith('test')

    def setUp(self):
        self.obj = QByteArray()
        self.orig_obj = QByteArray()


class ValidQByteArrayOperatorIAdd(unittest.TestCase, BaseQByteArrayOperatorIAdd):
    '''Test case for operator QByteArray += on valid QByteArrays'''

    doc_prefix = 'Valid object'
    doc_filter = lambda x: x.startswith('test')

    def setUp(self):
        self.obj = QByteArray(bytes('some byte array', "UTF-8"))
        self.orig_obj = QByteArray(bytes('some byte array', "UTF-8"))


if __name__ == '__main__':
    unittest.main()
