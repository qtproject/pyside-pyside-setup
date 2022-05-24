#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""
Unit tests for QTreeWidgetItem
------------------------------

This test is actually meant for all types which provide `tp_richcompare`
but actually define something without providing `==` or `!=` operators.
QTreeWidgetItem for instance defines `<` only.

PYSIDE-74: We redirect to type `object`s handling which is anyway the default
           when `tp_richcompare` is undefined.
"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem


class QTreeWidgetItemTest(unittest.TestCase):
    def testClass(self):
        app = QApplication([])
        treewidget = QTreeWidget()
        item = QTreeWidgetItem(["Words and stuff"])
        item2 = QTreeWidgetItem(["More words!"])
        treewidget.insertTopLevelItem(0, item)

        dummy_list = ["Numbers", "Symbols", "Spam"]
        self.assertFalse(item in dummy_list)
        self.assertTrue(item not in dummy_list)
        self.assertFalse(item == item2)
        self.assertTrue(item != item2)


if __name__ == "__main__":
    unittest.main()

