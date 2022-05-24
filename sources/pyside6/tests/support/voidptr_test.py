# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from shiboken6 import Shiboken
from PySide6.support import VoidPtr
from PySide6.QtCore import QByteArray


class PySide6Support(unittest.TestCase):

    def testVoidPtr(self):
        # Creating a VoidPtr object requires an address of
        # a C++ object, a wrapped Shiboken Object type,
        # an object implementing the Python Buffer interface,
        # or another VoidPtr object.

        # Original content
        b = b"Hello world"
        ba = QByteArray(b)
        vp = VoidPtr(ba, ba.size())
        self.assertIsInstance(vp, Shiboken.VoidPtr)

        # Create QByteArray from voidptr byte interpretation
        nba = QByteArray(vp.toBytes())
        # Compare original bytes to toBytes()
        self.assertTrue(b, vp.toBytes())
        # Compare original with new QByteArray data
        self.assertTrue(b, nba.data())
        # Convert original and new to str
        self.assertTrue(str(b), str(nba))

        # Modify nba through a memoryview of vp
        mv = memoryview(vp)
        self.assertFalse(mv.readonly)
        mv[6:11] = b'void*'
        self.assertEqual(str(ba), str(b"Hello void*"))


if __name__ == '__main__':
    unittest.main()
