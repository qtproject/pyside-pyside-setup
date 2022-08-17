# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QFormLayout, QWidget, QLabel, QMainWindow

from helper.usesqapplication import UsesQApplication


class QFormLayoutTest(UsesQApplication):

    def testGetItemPosition(self):
        formlayout = QFormLayout()

        row, role = formlayout.getItemPosition(0)
        self.assertTrue(isinstance(row, int))
        self.assertTrue(isinstance(role, QFormLayout.ItemRole))
        self.assertEqual(row, -1)

        widget = QWidget()
        formlayout.addRow(widget)
        row, role = formlayout.getItemPosition(0)
        self.assertTrue(isinstance(row, int))
        self.assertTrue(isinstance(role, QFormLayout.ItemRole))
        self.assertEqual(row, 0)
        self.assertEqual(role, QFormLayout.SpanningRole)

    def testGetWidgetPosition(self):
        formlayout = QFormLayout()
        widget = QWidget()

        row, role = formlayout.getWidgetPosition(widget)
        self.assertTrue(isinstance(row, int))
        self.assertTrue(isinstance(role, QFormLayout.ItemRole))
        self.assertEqual(row, -1)

        formlayout.addRow(widget)
        row, role = formlayout.getWidgetPosition(widget)
        self.assertTrue(isinstance(row, int))
        self.assertTrue(isinstance(role, QFormLayout.ItemRole))
        self.assertEqual(row, 0)
        self.assertEqual(role, QFormLayout.SpanningRole)

    def testGetLayoutPosition(self):
        formlayout = QFormLayout()
        layout = QFormLayout()

        row, role = formlayout.getLayoutPosition(layout)
        self.assertTrue(isinstance(row, int))
        self.assertTrue(isinstance(role, QFormLayout.ItemRole))
        self.assertEqual(row, -1)

        formlayout.addRow(layout)
        row, role = formlayout.getLayoutPosition(layout)
        self.assertTrue(isinstance(row, int))
        self.assertTrue(isinstance(role, QFormLayout.ItemRole))
        self.assertEqual(row, 0)
        self.assertEqual(role, QFormLayout.SpanningRole)

    def testTakeRow(self):
        window = QMainWindow()
        window.setCentralWidget(QWidget())
        formlayout = QFormLayout(window.centralWidget())

        widget_label = "blub"
        widget = QLabel(widget_label)

        self.assertEqual(formlayout.count(), 0)
        formlayout.addRow(widget)
        self.assertEqual(formlayout.count(), 1)
        self.assertEqual(formlayout.itemAt(0).widget(), widget)

        widget_id = id(widget)

        # Now there are no more references to the original widget on the
        # Python side. Assert that this does not break the references to
        # the widget on the C++ side so that "taking" the row will work.
        del widget

        takeRowResult = formlayout.takeRow(0)
        self.assertEqual(formlayout.count(), 0)

        widget = takeRowResult.fieldItem.widget()

        self.assertIsNotNone(widget)
        self.assertEqual(widget_id, id(widget))
        self.assertEqual(widget.text(), widget_label)


if __name__ == "__main__":
    unittest.main()
