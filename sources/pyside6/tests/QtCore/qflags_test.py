#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QFlags'''

import operator
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QTemporaryFile, QFile, QIODevice, QObject


class QFlagTest(unittest.TestCase):
    '''Test case for usage of flags'''

    def testCallFunction(self):
        f = QTemporaryFile()
        self.assertTrue(f.open())
        fileName = f.fileName()
        f.close()

        f = QFile(fileName)
        self.assertEqual(f.open(QIODevice.Truncate | QIODevice.Text | QIODevice.ReadWrite), True)
        om = f.openMode()
        self.assertEqual(om & QIODevice.Truncate, QIODevice.Truncate)
        self.assertEqual(om & QIODevice.Text, QIODevice.Text)
        self.assertEqual(om & QIODevice.ReadWrite, QIODevice.ReadWrite)
        self.assertTrue(om == QIODevice.Truncate | QIODevice.Text | QIODevice.ReadWrite)
        f.close()


class QFlagOperatorTest(unittest.TestCase):
    '''Test case for operators in QFlags'''

    def testInvert(self):
        '''QFlags ~ (invert) operator'''
        self.assertEqual(type(~QIODevice.ReadOnly), QIODevice.OpenMode)

    def testOr(self):
        '''QFlags | (or) operator'''
        self.assertEqual(type(QIODevice.ReadOnly | QIODevice.WriteOnly), QIODevice.OpenMode)

    def testAnd(self):
        '''QFlags & (and) operator'''
        self.assertEqual(type(QIODevice.ReadOnly & QIODevice.WriteOnly), QIODevice.OpenMode)

    def testIOr(self):
        '''QFlags |= (ior) operator'''
        flag = Qt.WindowFlags()
        self.assertTrue(Qt.Widget == 0)
        self.assertFalse(flag & Qt.Widget)
        result = flag & Qt.Widget
        self.assertTrue(result == 0)
        flag |= Qt.WindowMinimizeButtonHint
        self.assertTrue(flag & Qt.WindowMinimizeButtonHint)

    def testInvertOr(self):
        '''QFlags ~ (invert) operator over the result of an | (or) operator'''
        self.assertEqual(type(~(Qt.ItemIsSelectable | Qt.ItemIsEditable)), Qt.ItemFlags)

    def testEqual(self):
        '''QFlags == operator'''
        flags = Qt.Window
        flags |= Qt.WindowMinimizeButtonHint
        flag_type = (flags & Qt.WindowType_Mask)
        self.assertEqual(flag_type, Qt.Window)

        self.assertEqual(Qt.KeyboardModifiers(Qt.ControlModifier), Qt.ControlModifier)

    def testOperatorBetweenFlags(self):
        '''QFlags & QFlags'''
        flags = Qt.NoItemFlags | Qt.ItemIsUserCheckable
        newflags = Qt.NoItemFlags | Qt.ItemIsUserCheckable
        self.assertTrue(flags & newflags)

    def testOperatorDifferentOrder(self):
        '''Different ordering of arguments'''
        flags = Qt.NoItemFlags | Qt.ItemIsUserCheckable
        self.assertEqual(flags | Qt.ItemIsEnabled, Qt.ItemIsEnabled | flags)

    def testEqualNonNumericalObject(self):
        '''QFlags ==,!= non-numerical object '''
        flags = Qt.NoItemFlags | Qt.ItemIsUserCheckable

        self.assertTrue(flags != None)  # noqa: E711
        self.assertFalse(flags == None)  # noqa: E711

        self.assertTrue(flags != "tomato")
        self.assertFalse(flags == "tomato")

        with self.assertRaises(TypeError):
            flags > None
        with self.assertRaises(TypeError):
            flags >= None
        with self.assertRaises(TypeError):
            flags < None
        with self.assertRaises(TypeError):
            flags <= None


class QFlagsOnQVariant(unittest.TestCase):
    def testQFlagsOnQVariant(self):
        o = QObject()
        o.setProperty("foo", QIODevice.ReadOnly | QIODevice.WriteOnly)
        self.assertEqual(type(o.property("foo")), QIODevice.OpenMode)


class QFlagsWrongType(unittest.TestCase):
    @unittest.skipIf(sys.pyside63_option_python_enum, "Qt.ItemFlag is no longer an IntEnum")
    def testWrongType(self):
        '''Wrong type passed to QFlags binary operators'''
        for op in operator.or_, operator.and_, operator.xor:
            for x in '43', 'jabba', QObject, object:
                self.assertRaises(TypeError, op, Qt.NoItemFlags, x)
                self.assertRaises(TypeError, op, x, Qt.NoItemFlags)
        # making sure this actually does not fail all the time
        self.assertEqual(operator.or_(Qt.NoItemFlags, 43), 43)


class QEnumFlagDefault(unittest.TestCase):
    """
        Check that old flag and enum syntax can be used.
        The signatures of these surrogate functions intentionally do not exist
        because people should learn to use the new Enums correctly.
    """
    def testOldQFlag(self):
        self.assertEqual(Qt.AlignmentFlag(), Qt.AlignmentFlag(0))
        oldFlag = Qt.Alignment()
        oldEnum = Qt.AlignmentFlag()
        self.assertEqual(type(oldFlag), Qt.Alignment)
        self.assertEqual(type(oldEnum), Qt.AlignmentFlag)
        if sys.pyside63_option_python_enum:
            self.assertEqual(type(oldFlag), type(oldEnum))
        else:
            with self.assertRaises(AssertionError):
                self.assertEqual(type(oldFlag), type(oldEnum))


if __name__ == '__main__':
    unittest.main()
