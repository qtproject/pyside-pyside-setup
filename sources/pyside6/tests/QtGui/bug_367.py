# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 367: http://bugs.openbossa.org/show_bug.cgi?id=367'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtGui import QStandardItem, QStandardItemModel


class BugTest(UsesQApplication):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testCase(self):
        model = QStandardItemModel()
        parentItem = model.invisibleRootItem()
        for i in range(10):
            item = QStandardItem()
            rcount = sys.getrefcount(item)
            parentItem.appendRow(item)
            self.assertEqual(rcount + 1, sys.getrefcount(item))
            parentItem = item

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
