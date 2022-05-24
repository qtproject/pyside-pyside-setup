# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL


class QObjectDestroyed(unittest.TestCase):
    """Very simple test case for the destroyed() signal of QObject"""

    def setUp(self):
        self.called = False

    def destroyed_cb(self):
        self.called = True

    def testDestroyed(self):
        """Emission of QObject.destroyed() to a python slot"""
        obj = QObject()
        obj.destroyed.connect(self.destroyed_cb)
        del obj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
