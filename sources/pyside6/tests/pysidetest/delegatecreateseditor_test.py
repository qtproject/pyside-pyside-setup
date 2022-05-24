#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from helper.usesqapplication import UsesQApplication
from testbinding import TestView
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (QAbstractItemDelegate, QComboBox,
                               QSpinBox, QStyledItemDelegate,
                               QStyleOptionViewItem, QWidget)

id_text = 'This is me'


class DelegateDoesntKeepReferenceToEditor(QAbstractItemDelegate):
    def createEditor(self, parent, option, index):
        comboBox = QComboBox(parent)
        comboBox.addItem(id_text)
        return comboBox


class DelegateKeepsReferenceToEditor(QAbstractItemDelegate):
    def __init__(self, parent=None):
        QAbstractItemDelegate.__init__(self, parent)
        self.comboBox = QComboBox()
        self.comboBox.addItem(id_text)

    def createEditor(self, parent, option, index):
        self.comboBox.setParent(parent)
        return self.comboBox


class EditorCreatedByDelegateTest(UsesQApplication):

    def testDelegateDoesntKeepReferenceToEditor(self):
        view = TestView(None)
        delegate = DelegateDoesntKeepReferenceToEditor()
        view.setItemDelegate(delegate)
        editor = view.getEditorWidgetFromItemDelegate()
        self.assertEqual(type(editor), QComboBox)
        self.assertEqual(editor.count(), 1)
        self.assertEqual(editor.itemData(0, Qt.DisplayRole), id_text)
        editor.metaObject()

    def testDelegateKeepsReferenceToEditor(self):
        view = TestView(None)
        delegate = DelegateKeepsReferenceToEditor()
        view.setItemDelegate(delegate)
        editor = view.getEditorWidgetFromItemDelegate()
        self.assertEqual(type(editor), QComboBox)
        self.assertEqual(editor.count(), 1)
        self.assertEqual(editor.itemData(0, Qt.DisplayRole), id_text)
        editor.metaObject()

    def testIntDelegate(self):
        """PYSIDE-1250: When creating a QVariant, use int instead of long long
           for anything that fits into a int. Verify by checking that a spin
           box is created as item view editor for int."""
        item = QStandardItem()
        item.setData(123123, Qt.EditRole)  # <-- QVariant conversion here
        model = QStandardItemModel()
        model.appendRow(item)
        style_option = QStyleOptionViewItem()
        delegate = QStyledItemDelegate()
        editor = delegate.createEditor(None, style_option, model.index(0, 0))
        self.assertEqual(type(editor), QSpinBox)


if __name__ == '__main__':
    unittest.main()

