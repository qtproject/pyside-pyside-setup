#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QBuffer
from PySide6.QtSvg import QSvgGenerator


class QSvgGeneratorTest(unittest.TestCase):

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefCountOfTOutputDevice(self):
        generator = QSvgGenerator()
        iodevice1 = QBuffer()
        refcount1 = sys.getrefcount(iodevice1)

        generator.setOutputDevice(iodevice1)

        self.assertEqual(generator.outputDevice(), iodevice1)
        self.assertEqual(sys.getrefcount(generator.outputDevice()), refcount1 + 1)

        iodevice2 = QBuffer()
        refcount2 = sys.getrefcount(iodevice2)

        generator.setOutputDevice(iodevice2)

        self.assertEqual(generator.outputDevice(), iodevice2)
        self.assertEqual(sys.getrefcount(generator.outputDevice()), refcount2 + 1)
        self.assertEqual(sys.getrefcount(iodevice1), refcount1)

        del generator

        self.assertEqual(sys.getrefcount(iodevice2), refcount2)


if __name__ == '__main__':
    unittest.main()

