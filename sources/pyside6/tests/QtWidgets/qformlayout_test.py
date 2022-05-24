# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QFormLayout, QWidget

from helper.usesqapplication import UsesQApplication


class QFormLayoutTest(UsesQApplication):

    def testGetItemPosition(self):
        formlayout = QFormLayout()
        if not sys.pyside63_option_python_enum:
            # PYSIDE-1735: This gives random values if no row exists.
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
        if not sys.pyside63_option_python_enum:
            # PYSIDE-1735: This gives random values if no row exists.
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
        if not sys.pyside63_option_python_enum:
            # PYSIDE-1735: This gives random values if no row exists.
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


if __name__ == "__main__":
    unittest.main()

