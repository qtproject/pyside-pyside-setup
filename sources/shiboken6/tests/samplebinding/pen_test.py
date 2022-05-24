#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for <add-function> with const char* as argument'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Color, Pen, SampleNamespace

class TestPen(unittest.TestCase):
    '''Simple test case for Pen.'''

    def testPenWithEmptyConstructor(self):
        pen = Pen()
        self.assertEqual(pen.ctorType(), Pen.EmptyCtor)

    def testPenWithEnumConstructor(self):
        pen = Pen(SampleNamespace.RandomNumber)
        self.assertEqual(pen.ctorType(), Pen.EnumCtor)

    def testPenWithColorConstructor(self):
        pen = Pen(Color())
        self.assertEqual(pen.ctorType(), Pen.ColorCtor)

    def testPenWithCopyConstructor(self):
        pen = Pen(Pen())
        self.assertEqual(pen.ctorType(), Pen.CopyCtor)

    def testPenWithIntConvertedToColor(self):
        pen = Pen(1)
        self.assertEqual(pen.ctorType(), Pen.ColorCtor)
        pen.drawLine(0, 0, 5, 5)

    def testPenRenderHintsProperty(self):
        """Exercise the generated property setter and getters, checking
           against the C++ getter/setter functions."""
        pen = Pen(1)
        self.assertEqual(pen.getRenderHints(), Pen.RenderHints.None_)
        self.assertEqual(pen.renderHints, Pen.RenderHints.None_)
        pen.renderHints = Pen.RenderHints.TextAntialiasing
        self.assertEqual(pen.getRenderHints(), Pen.RenderHints.TextAntialiasing)
        self.assertEqual(pen.renderHints, Pen.RenderHints.TextAntialiasing)
        pen.setRenderHints(Pen.RenderHints.Antialiasing)
        self.assertEqual(pen.getRenderHints(), Pen.RenderHints.Antialiasing)
        self.assertEqual(pen.renderHints, Pen.RenderHints.Antialiasing)


if __name__ == '__main__':
    unittest.main()
