#!/usr/bin/env python
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

from PySide6.QtCore import QObject


class DisconnectSignalsTest(unittest.TestCase):

    def setUp(self):
        self.emitter = QObject()

    def tearDown(self):
        del self.emitter
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testConnectionRefCount(self):

        def destroyedSlot():
            pass

        self.assertEqual(sys.getrefcount(destroyedSlot), 2)
        self.emitter.destroyed.connect(destroyedSlot)
        self.assertEqual(sys.getrefcount(destroyedSlot), 3)
        self.emitter.destroyed.disconnect(destroyedSlot)
        self.assertEqual(sys.getrefcount(destroyedSlot), 2)


if __name__ == '__main__':
    unittest.main()

