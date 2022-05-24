#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QUrlQuery'''

import ctypes
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUrlQuery


class QUrlQueryTest(unittest.TestCase):
    def testConstructing(self):
        empty = QUrlQuery()
        self.assertTrue(empty.isEmpty())

        empty.clear()
        self.assertTrue(empty.isEmpty())

    def testAddRemove(self):
        query = QUrlQuery()

        query.addQueryItem("a", "b")
        self.assertTrue(not query.isEmpty())
        self.assertTrue(query.hasQueryItem("a"))
        self.assertEqual(query.queryItemValue("a"), "b")
        self.assertEqual(query.allQueryItemValues("a"), ["b"])


if __name__ == '__main__':
    unittest.main()
