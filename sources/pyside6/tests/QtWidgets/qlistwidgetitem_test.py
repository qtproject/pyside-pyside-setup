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

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from helper.usesqapplication import UsesQApplication


class QListWidgetItemConstructor(UsesQApplication):

    def setUp(self):
        super(QListWidgetItemConstructor, self).setUp()
        self.widgetList = QListWidget()

    def tearDown(self):
        del self.widgetList
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(QListWidgetItemConstructor, self).tearDown()

    def testConstructorWithParent(self):
        # Bug 235 - QListWidgetItem constructor not saving ownership
        QListWidgetItem(self.widgetList)
        item = self.widgetList.item(0)
        self.assertEqual(item.listWidget(), self.widgetList)

    def testConstructorWithNone(self):
        # Bug 452 - QListWidgetItem() not casting NoneType to null correctly.
        item = QListWidgetItem(None, 123)


if __name__ == '__main__':
    unittest.main()
