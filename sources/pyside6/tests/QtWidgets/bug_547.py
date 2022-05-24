# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

""" Unittest for bug #547 """
""" http://bugs.openbossa.org/show_bug.cgi?id=547 """

import sys
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem


class MyMainWindow(unittest.TestCase):
    app = QApplication(sys.argv)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testCase1(self):
        self._tree = QTreeWidget()
        self._tree.setColumnCount(2)
        self._i1 = None
        self._i11 = None

        self._updateTree()
        self.assertEqual(sys.getrefcount(self._i1), 3)
        self.assertEqual(sys.getrefcount(self._i11), 3)

        self._i11.parent().setExpanded(True)
        self._i11.setExpanded(True)

        self._updateTree()
        self.assertEqual(sys.getrefcount(self._i1), 3)
        self.assertEqual(sys.getrefcount(self._i11), 3)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testCase2(self):
        self._tree = QTreeWidget()
        self._tree.setColumnCount(2)
        self._i1 = None
        self._i11 = None

        self._updateTree()
        self.assertEqual(sys.getrefcount(self._i1), 3)
        self.assertEqual(sys.getrefcount(self._i11), 3)

        self._i11.parent().setExpanded(True)
        self._i11.setExpanded(True)

        self.assertEqual(sys.getrefcount(self._i1), 3)
        self.assertEqual(sys.getrefcount(self._i11), 3)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def _updateTree(self):
        self._tree.clear()
        if self._i1 and self._i11:
            self.assertEqual(sys.getrefcount(self._i1), 2)
            self.assertEqual(sys.getrefcount(self._i11), 2)

        self._i1 = QTreeWidgetItem(self._tree, ['1', ])
        self.assertEqual(sys.getrefcount(self._i1), 3)
        self._i11 = QTreeWidgetItem(self._i1, ['11', ])
        self.assertEqual(sys.getrefcount(self._i11), 3)


if __name__ == '__main__':
    unittest.main()

