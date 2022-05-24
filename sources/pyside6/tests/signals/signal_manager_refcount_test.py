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

from PySide6.QtCore import QObject, SIGNAL


class SignalManagerRefCount(unittest.TestCase):
    """Simple test case to check if the signal_manager is erroneously incrementing the object refcounter"""

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testObjectRefcount(self):
        """Emission of QObject.destroyed() to a python slot"""
        def callback():
            pass
        obj = QObject()
        refcount = sys.getrefcount(obj)
        obj.destroyed.connect(callback)
        self.assertEqual(refcount, sys.getrefcount(obj))
        QObject.disconnect(obj, SIGNAL('destroyed()'), callback)
        self.assertEqual(refcount, sys.getrefcount(obj))


if __name__ == '__main__':
    unittest.main()

