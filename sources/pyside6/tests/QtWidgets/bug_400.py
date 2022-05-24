# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 400: http://bugs.openbossa.org/show_bug.cgi?id=400'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtWidgets import QTreeWidgetItemIterator, QTreeWidgetItem, QTreeWidget


class BugTest(UsesQApplication):
    def testCase(self):
        treeWidget = QTreeWidget()
        treeWidget.setColumnCount(1)
        items = []
        for i in range(10):
            items.append(QTreeWidgetItem(None, [f"item: {i}"]))

        treeWidget.insertTopLevelItems(0, items)
        _iter = QTreeWidgetItemIterator(treeWidget)
        index = 0
        while(_iter.value()):
            item = _iter.value()
            self.assertTrue(item is items[index])
            index += 1
            _iter += 1


if __name__ == '__main__':
    unittest.main()
