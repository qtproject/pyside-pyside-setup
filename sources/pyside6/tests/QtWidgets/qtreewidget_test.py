# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QPushButton
from helper.usesqapplication import UsesQApplication


class QTreeWidgetTest(UsesQApplication):

    # PYSIDE-73:
    #   There was a problem when adding items to a QTreeWidget
    #   when the Widget was being build on the method call instead
    #   of as a separate variable.
    #   The problem was there was not ownership transfer, so the
    #   QTreeWidget did not own the QWidget element
    def testSetItemWidget(self):

        treeWidget = QTreeWidget()
        treeWidget.setColumnCount(2)

        item = QTreeWidgetItem(['text of column 0', ''])
        treeWidget.insertTopLevelItem(0, item)
        # Adding QPushButton inside the method
        treeWidget.setItemWidget(item, 1,
            QPushButton('Push button on column 1'))

        # Getting the widget back
        w = treeWidget.itemWidget(treeWidget.itemAt(0, 1), 1)
        self.assertIsInstance(w, QPushButton)

        p = QPushButton('New independent button')
        # Adding QPushButton object from variable
        treeWidget.setItemWidget(item, 0, p)
        w = treeWidget.itemWidget(treeWidget.itemAt(0, 0), 0)
        self.assertIsInstance(w, QPushButton)


if __name__ == '__main__':
    unittest.main()
