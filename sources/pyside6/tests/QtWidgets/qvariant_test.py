#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
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
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QObject
from PySide6.QtWidgets import (QComboBox, QGraphicsScene,
    QGraphicsRectItem, QComboBox)

from helper.usesqapplication import UsesQApplication


class MyDiagram(QGraphicsScene):
    pass


class MyItem(QGraphicsRectItem):
    def itemChange(self, change, value):
        return value


class Sequence(object):
    # Having the __getitem__ method on a class transform the Python
    # type to a PySequence.
    # Before the patch: aa75437f9119d997dd290471ac3e2cc88ca88bf1
    # "Fix QVariant conversions when using PySequences"
    # one could not use an object from this class, because internally
    # we were requiring that the PySequence was finite.
    def __getitem__(self, key):
        raise IndexError()


class QGraphicsSceneOnQVariantTest(UsesQApplication):
    """Test storage ot QGraphicsScene into QVariants"""
    def setUp(self):
        super(QGraphicsSceneOnQVariantTest, self).setUp()
        self.s = MyDiagram()
        self.i = MyItem()
        self.combo = QComboBox()

    def tearDown(self):
        del self.s
        del self.i
        del self.combo
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(QGraphicsSceneOnQVariantTest, self).tearDown()

    def testIt(self):
        self.s.addItem(self.i)
        self.assertEqual(len(self.s.items()), 1)

    def testSequence(self):
        # PYSIDE-641
        self.combo.addItem("test", userData=Sequence())
        self.assertTrue(isinstance(self.combo.itemData(0), Sequence))


class QVariantConversionTest(UsesQApplication):
    """
    Tests conversion from QVariant to supported type held by QVariant
    """
    def setUp(self):
        super(QVariantConversionTest, self).setUp()
        self.obj = QObject()

    def tearDown(self):
        del self.obj
        super(QVariantConversionTest, self).tearDown()

    def testEnum(self):
        """
        PYSIDE-1798: Test enum is obtained correctly when return through QVariant
        """
        self.obj.setProperty("test", Qt.SolidLine)
        self.assertTrue(isinstance(self.obj.property("test"), Qt.PenStyle))
        self.assertEqual(self.obj.property("test"), Qt.SolidLine)

    def testString(self):
        self.obj.setProperty("test", "test")
        self.assertEqual(self.obj.property("test"), "test")
        self.assertTrue(isinstance(self.obj.property("test"), str))

    def testBytes(self):
        byte_message = bytes("test", 'utf-8')
        self.obj.setProperty("test", byte_message)
        self.assertEqual(self.obj.property("test"), byte_message)
        self.assertTrue(isinstance(self.obj.property("test"), bytes))

    def testBasicTypes(self):
        #bool
        self.obj.setProperty("test", True)
        self.assertEqual(self.obj.property("test"), True)
        self.assertTrue(isinstance(self.obj.property("test"), bool))
        #long
        self.obj.setProperty("test", 2)
        self.assertEqual(self.obj.property("test"), 2)
        self.assertTrue(isinstance(self.obj.property("test"), int))
        #float
        self.obj.setProperty("test", 2.5)
        self.assertEqual(self.obj.property("test"), 2.5)
        self.assertTrue(isinstance(self.obj.property("test"), float))
        #None
        self.obj.setProperty("test", None)
        self.assertEqual(self.obj.property("test"), None)

    def testContainerTypes(self):
        #list
        self.obj.setProperty("test", [1,2,3])
        self.assertEqual(self.obj.property("test"), [1,2,3])
        self.assertTrue(isinstance(self.obj.property("test"), list))
        #dict
        self.obj.setProperty("test", {1: "one"})
        self.assertEqual(self.obj.property("test"), {1: "one"})
        self.assertTrue(isinstance(self.obj.property("test"), dict))

    def testPyObject(self):
        class Test:
            pass
        test = Test()
        self.obj.setProperty("test", test)
        self.assertEqual(self.obj.property("test"), test)
        self.assertTrue(isinstance(self.obj.property("test"), Test))


if __name__ == '__main__':
    unittest.main()
