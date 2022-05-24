# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QTableWidgetItem, QListWidgetItem, QTreeWidgetItem


class TestBug569(unittest.TestCase):

    def testIt(self):
        types = (QTableWidgetItem, QListWidgetItem, QTreeWidgetItem)
        for t in types:
            a = t()
            a.__lt__ = lambda other: True
            b = t()
            b.__lt__ = lambda other: False
            self.assertTrue(a < b)
            self.assertFalse(b < a)


if __name__ == '__main__':
    unittest.main()
