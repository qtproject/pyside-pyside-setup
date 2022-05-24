# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""
iterable_test.py

This test checks that the Iterable protocol is implemented correctly.
"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6
from PySide6 import QtCore, QtGui

try:
    import numpy as np
    have_numpy = True
except ImportError:
    have_numpy = False


class PySequenceTest(unittest.TestCase):

    def test_iterable(self):
        def gen(lis):
            for item in lis:
                if item == "crash":
                    raise IndexError
                yield item
        # testing "pyseq_to_cpplist_conversion"
        testfunc = QtCore.QUrl.fromStringList
        # use a generator (iterable)
        self.assertEqual(testfunc(gen(["asd", "ghj"])),
            [PySide6.QtCore.QUrl('asd'), PySide6.QtCore.QUrl('ghj')])
        # use an iterator
        self.assertEqual(testfunc(iter(["asd", "ghj"])),
            [PySide6.QtCore.QUrl('asd'), PySide6.QtCore.QUrl('ghj')])
        self.assertRaises(IndexError, testfunc, gen(["asd", "crash", "ghj"]))
        # testing QMatrix4x4
        testfunc = QtGui.QMatrix4x4
        self.assertEqual(testfunc(gen(range(16))), testfunc(range(16)))
        # Note: The errormessage needs to be improved!
        # We should better get a ValueError
        self.assertRaises((TypeError, ValueError), testfunc, gen(range(15)))
        # All other matrix sizes:
        testfunc = QtGui.QMatrix2x2
        self.assertEqual(testfunc(gen(range(4))), testfunc(range(4)))
        testfunc = QtGui.QMatrix2x3
        self.assertEqual(testfunc(gen(range(6))), testfunc(range(6)))

    @unittest.skipUnless(have_numpy, "requires numpy")
    def test_iterable_numpy(self):
        # Demo for numpy: We create a unit matrix.
        num_mat = np.eye(4)
        num_mat.shape = 16
        unit = QtGui.QMatrix4x4(num_mat)
        self.assertEqual(unit, QtGui.QMatrix4x4())


if __name__ == '__main__':
    unittest.main()
