# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QGridLayout, QHBoxLayout, QWidget

from helper.timedqapplication import TimedQApplication


class LabelWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.test_layout = QGridLayout()
        label = QLabel("Label")
        self.test_layout.addWidget(label, 0, 0)
        self.setLayout(self.test_layout)
        self._destroyCalled = False

    def replace(self, unit):
        old_item = self.test_layout.itemAtPosition(0, 0)
        old_label = old_item.widget()
        ref = weakref.ref(old_item, self._destroyed)

        self.test_layout.removeWidget(old_label)
        unit.assertRaises(RuntimeError, old_item.widget)
        del old_item
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

        label = QLabel("Label New")
        old_label.deleteLater()
        label.setAlignment(Qt.AlignCenter)
        self.test_layout.addWidget(label, 0, 0)

    def _destroyed(self, obj):
        self._destroyCalled = True


class TestBug1006 (TimedQApplication):

    def testLayoutItemLifeTime(self):
        window = LabelWindow(None)
        window.replace(self)
        self.assertTrue(window._destroyCalled)
        self.app.exec()

    def testParentLayout(self):
        def createLayout():
            label = QLabel()
            layout = QHBoxLayout()
            layout.addWidget(label)

            widget = QWidget()
            widget.setLayout(layout)
            return (layout, widget)
        (layout, widget) = createLayout()
        item = layout.itemAt(0)
        self.assertTrue(isinstance(item.widget(), QWidget))

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRemoveOrphanWidget(self):
        widget = QLabel()
        layout = QHBoxLayout()
        layout.addWidget(widget)
        self.assertEqual(sys.getrefcount(widget), 3)

        layout.removeWidget(widget)
        widget.setObjectName("MyWidget")
        self.assertEqual(sys.getrefcount(widget), 2)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRemoveChildWidget(self):
        parent = QLabel()
        widget = QLabel(parent)
        self.assertEqual(sys.getrefcount(widget), 3)

        layout = QHBoxLayout()
        layout.addWidget(widget)
        self.assertEqual(sys.getrefcount(widget), 3)

        layout.removeWidget(widget)
        widget.setObjectName("MyWidget")
        self.assertEqual(sys.getrefcount(widget), 3)


if __name__ == "__main__":
    unittest.main()
