# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test bug 585: http://bugs.openbossa.org/show_bug.cgi?id=585'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem


class Bug585(unittest.TestCase):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testCase(self):
        app = QApplication([])
        self._tree = QTreeWidget()
        self._tree.setColumnCount(2)
        i1 = QTreeWidgetItem(self._tree, ['1', ])
        i2 = QTreeWidgetItem(self._tree, ['2', ])
        refCount = sys.getrefcount(i1)

        # this function return None
        # because the topLevelItem does not has a parent item
        # but still have a TreeWidget as a parent
        self._tree.topLevelItem(0).parent()

        self.assertEqual(refCount, sys.getrefcount(i1))


if __name__ == '__main__':
    unittest.main()

