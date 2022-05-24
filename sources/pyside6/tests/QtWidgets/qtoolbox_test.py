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

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolBox, QWidget

from helper.usesqapplication import UsesQApplication


class OwnershipControl(UsesQApplication):

    def setUp(self):
        super(OwnershipControl, self).setUp()
        self.toolbox = QToolBox()

    def tearDown(self):
        del self.toolbox
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(OwnershipControl, self).tearDown()

    def testAddItem(self):
        # Was losing ownership of the widget.
        index = self.toolbox.addItem(QWidget(), 'item')
        item = self.toolbox.widget(index)
        self.assertTrue(isinstance(item, QWidget))

    def testAddItemWithIcon(self):
        index = self.toolbox.addItem(QWidget(), QIcon(), 'item')
        item = self.toolbox.widget(index)
        self.assertTrue(isinstance(item, QWidget))


if __name__ == '__main__':
    unittest.main()
