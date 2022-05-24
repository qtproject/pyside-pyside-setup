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

from PySide6.QtCore import QT_TR_NOOP, QT_TR_NOOP_UTF8
from PySide6.QtCore import QT_TRANSLATE_NOOP, QT_TRANSLATE_NOOP3, QT_TRANSLATE_NOOP_UTF8


class QtTrNoopTest(unittest.TestCase):

    def setUp(self):
        self.txt = 'Cthulhu fhtag!'

    def tearDown(self):
        del self.txt
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testQtTrNoop(self):
        refcnt = sys.getrefcount(self.txt)
        result = QT_TR_NOOP(self.txt)
        self.assertEqual(result, self.txt)
        self.assertEqual(sys.getrefcount(result), refcnt + 1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testQtTrNoopUtf8(self):
        refcnt = sys.getrefcount(self.txt)
        result = QT_TR_NOOP_UTF8(self.txt)
        self.assertEqual(result, self.txt)
        self.assertEqual(sys.getrefcount(result), refcnt + 1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testQtTranslateNoop(self):
        refcnt = sys.getrefcount(self.txt)
        result = QT_TRANSLATE_NOOP(None, self.txt)
        self.assertEqual(result, self.txt)
        self.assertEqual(sys.getrefcount(result), refcnt + 1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testQtTranslateNoopUtf8(self):
        refcnt = sys.getrefcount(self.txt)
        result = QT_TRANSLATE_NOOP_UTF8(self.txt)
        self.assertEqual(result, self.txt)
        self.assertEqual(sys.getrefcount(result), refcnt + 1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testQtTranslateNoop3(self):
        refcnt = sys.getrefcount(self.txt)
        result = QT_TRANSLATE_NOOP3(None, self.txt, None)
        self.assertEqual(result, self.txt)
        self.assertEqual(sys.getrefcount(result), refcnt + 1)


if __name__ == '__main__':
    unittest.main()

