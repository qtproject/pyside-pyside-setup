#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for method arguments modifications performed as described on typesystem.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Modifications, Point


class ArgumentModificationsTest(unittest.TestCase):
    '''Test cases for method arguments modifications performed as described on typesystem.'''

    def setUp(self):
        self.mods = Modifications()

    def tearDown(self):
        del self.mods
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testArgRemoval0(self):
        '''Tests argument removal modifications on Modifications.argRemoval0.'''
        # void [-> PyObject*] argRemoval0(int, bool, int = 123 [removed, new val = 321], int = 456)
        # code-injection: returns tuple with received parameters plus removed ones
        a0, a1, a2 = 1, True, 2
        self.assertEqual(self.mods.argRemoval0(a0, a1), (a0, a1, 321, 456))
        self.assertEqual(self.mods.argRemoval0(a0, a1, a2), (a0, a1, 321, a2))
        # the other wasn't modified
        # void argRemoval0(int, bool, int, bool)
        self.assertEqual(self.mods.argRemoval0(0, False, 0, False), None)

    def testArgRemoval1(self):
        '''Tests argument removal modifications on Modifications.argRemoval1.'''
        # void [-> PyObject*] argRemoval1(int, bool, Point = Point(1, 2) [removed],
        #      Point = Point(3, 4) [removed], int = 333)
        # code-injection: returns tuple with received parameters plus removed ones
        a0, a1, a2 = 1, True, 2
        self.assertEqual(self.mods.argRemoval1(a0, a1), (a0, a1, Point(1, 2), Point(3, 4), 333))
        self.assertEqual(self.mods.argRemoval1(a0, a1, a2), (a0, a1, Point(1, 2), Point(3, 4), a2))
        # the other wasn't modified
        # void argRemoval1(int, bool, int, bool)
        self.assertEqual(self.mods.argRemoval1(0, False, 0, False), None)

    def testArgRemoval2(self):
        '''Tests argument removal modifications on Modifications.argRemoval2.'''
        # void [-> PyObject*] argRemoval2(int, bool, Point = Point(1, 2)
        #      [removed], Point = Point(3, 4) [removed], int = 333)
        # code-injection: returns tuple with received parameters plus removed ones
        a0, a1, a2 = 1, True, 2
        self.assertEqual(self.mods.argRemoval2(a0, a1), (a0, a1, Point(1, 2), Point(3, 4), 333))
        self.assertEqual(self.mods.argRemoval2(a0, a1, a2), (a0, a1, Point(1, 2), Point(3, 4), a2))

    def testArgRemoval3(self):
        '''Tests argument removal modifications on Modifications.argRemoval3.'''
        # void [-> PyObject*] argRemoval3(int, Point = Point(1, 2) [removed],
        #      bool = true, Point = Point(3, 4) [removed], int = 333)
        # code-injection: returns tuple with received parameters plus removed ones
        a0, a1, a2 = 1, True, 2
        self.assertEqual(self.mods.argRemoval3(a0), (a0, Point(1, 2), True, Point(3, 4), 333))
        self.assertEqual(self.mods.argRemoval3(a0, a1), (a0, Point(1, 2), a1, Point(3, 4), 333))
        self.assertEqual(self.mods.argRemoval3(a0, a1, a2), (a0, Point(1, 2), a1, Point(3, 4), a2))

    def testArgRemoval4(self):
        '''Tests argument removal modifications on Modifications.argRemoval4.'''
        # void [-> PyObject*] argRemoval4(int, Point [removed, new val = Point(6, 9)], bool,
        #      Point = Point(3, 4) [removed], int = 333)
        # code-injection: returns tuple with received parameters plus removed ones
        a0, a1, a2 = 1, True, 2
        self.assertRaises(TypeError, self.mods.argRemoval4, a0)
        self.assertEqual(self.mods.argRemoval4(a0, a1), (a0, Point(6, 9), a1, Point(3, 4), 333))
        self.assertEqual(self.mods.argRemoval4(a0, a1, a2), (a0, Point(6, 9), a1, Point(3, 4), a2))

    def testArgRemoval5(self):
        '''Tests argument removal modifications on Modifications.argRemoval5.'''
        # void [-> PyObject*] argRemoval5(int [removed, new val = 100], bool,
        #                                 Point = Point(1, 2) [removed],
        #                                 Point = Point(3, 4) [removed], int = 333)
        # code-injection: returns tuple with received parameters plus removed ones
        a0, a1, a2 = True, 2, True
        self.assertEqual(self.mods.argRemoval5(a0), (100, a0, Point(1, 2), Point(3, 4), 333))
        self.assertEqual(self.mods.argRemoval5(a0, a1), (100, a0, Point(1, 2), Point(3, 4), a1))
        # void [-> PyObject*] argRemoval5(int [removed, new val = 200], bool, int, bool)
        # code-injection: returns tuple with received parameters plus removed ones
        self.assertEqual(self.mods.argRemoval5(a0, a1, a2), (200, a0, a1, a2))


if __name__ == '__main__':
    unittest.main()
