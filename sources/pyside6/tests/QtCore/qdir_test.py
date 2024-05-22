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

from PySide6.QtCore import QDir, QDirListing


class QDirTest(unittest.TestCase):
    '''Test case for QDir'''

    def testConstructor(self):
        # Optional case without arguments is equivalent to the constructor
        #    QDir(const QString &path = QString())
        a = QDir()

        self.assertTrue(a.isReadable())
        self.assertTrue(a.isRelative())

        # Empty string
        b = QDir("")
        self.assertEqual(a, b)

        # Empty Path
        c = QDir(Path())
        self.assertEqual(a, c)

        self.assertEqual(b, c)


class QDirListingTest(unittest.TestCase):
    '''Test case for QDirListing'''

    def test(self):
        dir_listing = QDirListing(QDir.homePath())
        for entry in dir_listing:
            pass


if __name__ == '__main__':
    unittest.main()
