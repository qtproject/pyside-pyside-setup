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
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import QObject

from testbinding import SharedPointerTestbench, QSharedPointer_QObject


def create_qobject(name):
    result = QObject()
    result.setObjectName(name)
    return result


class SharedPointerTests(unittest.TestCase):

    def testObjSharedPointer(self):
        p = SharedPointerTestbench.createSharedPointerQObject()
        self.assertEqual(p.objectName(), "TestObject")
        SharedPointerTestbench.printSharedPointerQObject(p)

    def testIntSharedPointer(self):
        p = SharedPointerTestbench.createSharedPointerInt(42)
        SharedPointerTestbench.printSharedPointerInt(p)

    def testConstruction(self):
        name1 = "CreatedQObject1"
        p1 = QSharedPointer_QObject(create_qobject(name1))
        self.assertTrue(p1)
        self.assertEqual(p1.objectName(), name1)

        p1.reset()
        self.assertFalse(p1)

        name2 = "CreatedQObject2"
        p1.reset(create_qobject(name2))
        self.assertTrue(p1)
        self.assertEqual(p1.objectName(), name2)


if __name__ == '__main__':
    unittest.main()
