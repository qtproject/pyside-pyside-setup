# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

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
        p = SharedPointerTestbench.createSharedPointerConstQObject()
        SharedPointerTestbench.printSharedPointerConstQObject(p)

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
