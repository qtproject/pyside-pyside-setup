# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QGraphicsScene


class TestBug679(unittest.TestCase):
    '''QGraphicsScene::clear() is missing'''
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testIt(self):
        app = QApplication([])  # noqa: F841

        scene = QGraphicsScene()
        hello = scene.addText("Hello")
        base_ref_count = sys.getrefcount(hello)
        scene.addText("World")

        scene.clear()
        self.assertEqual(sys.getrefcount(hello), base_ref_count - 1)
        self.assertEqual(len(scene.items()), 0)
        self.assertRaises(RuntimeError, hello.isVisible)  # the C++ object was deleted


if __name__ == '__main__':
    unittest.main()
