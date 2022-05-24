#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import TestObject
from PySide6.QtWidgets import QApplication
from PySide6 import __all__ as all


class QApplicationInstance(unittest.TestCase):

    def appDestroyed(self):
        self.assertTrue(False)

    def testInstanceObject(self):
        self.assertEqual(type(qApp), type(None))
        TestObject.createApp()
        app1 = QApplication.instance()
        app2 = QApplication.instance()
        app1.setObjectName("MyApp")
        self.assertEqual(app1, app2)
        self.assertEqual(app2.objectName(), app1.objectName())
        # We no longer support qApp when embedding
        # if len(all) > 3:
        #     # an import triggers qApp initialization
        #     __import__("PySide6." + all[-1])
        #     self.assertEqual(app1, qApp)
        app1.destroyed.connect(self.appDestroyed)


if __name__ == '__main__':
    unittest.main()

