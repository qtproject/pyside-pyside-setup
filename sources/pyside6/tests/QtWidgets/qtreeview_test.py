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

from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import (QWidget, QTreeView, QVBoxLayout,
    QStyledItemDelegate, QHeaderView)
from PySide6.QtCore import Qt
from helper.usesqapplication import UsesQApplication


class Widget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.treeView = QTreeView(self)
        layout = QVBoxLayout()
        layout.addWidget(self.treeView)
        self.setLayout(layout)
        self.treeView.setModel(QStandardItemModel())

        self.treeView.model().setHorizontalHeaderLabels(('3', '1', '5'))


class QWidgetTest(UsesQApplication):

    def testDelegates(self):
        widget = Widget()
        t = widget.treeView

        # When calling setItemDelegateForColumn using a separate variable
        # for the second argument (QAbstractItemDelegate), there was no problem
        # on keeping the reference to this object, since the variable was kept
        # alive (case A)
        # Contrary, when instantiating this argument on the function call
        # Using QStyledItemDelegate inside the call the reference of the
        # object was lost, causing a segfault. (case B)

        # Case A
        d = QStyledItemDelegate()
        # Using QStyledItemDelegate from a variable so we keep the reference alive
        # and we encounter no segfault.
        t.setItemDelegateForColumn(0, d)
        # This raised the Segmentation Fault too, because manually destroying
        # the object caused a missing refrence.
        del d
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

        # Getting the delegates
        a = t.itemDelegateForColumn(0)
        self.assertIsInstance(a, QStyledItemDelegate)

        # Case B
        t.setItemDelegateForColumn(1, QStyledItemDelegate())

        # Getting the delegates
        b = t.itemDelegateForColumn(1)
        self.assertIsInstance(b, QStyledItemDelegate)

        # Test for Rows
        t.setItemDelegateForRow(0, QStyledItemDelegate())
        self.assertIsInstance(t.itemDelegateForRow(0), QStyledItemDelegate)

        # Test for general delegate
        t.setItemDelegate(QStyledItemDelegate())
        self.assertIsInstance(t.itemDelegate(), QStyledItemDelegate)

    def testHeader(self):
        tree = QTreeView()
        tree.setHeader(QHeaderView(Qt.Horizontal))
        self.assertIsNotNone(tree.header())


if __name__ == '__main__':
    unittest.main()
