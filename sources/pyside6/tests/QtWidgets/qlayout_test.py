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

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QFormLayout, QHBoxLayout, QLayout, QPushButton,
                               QSpacerItem, QWidget, QWidgetItem)


class MyLayout(QLayout):
    def __init__(self, parent=None):
        QLayout.__init__(self, parent)
        self._list = []

    def addItem(self, item):
        self.add(item)

    def addWidget(self, widget):
        self.add(QWidgetItem(widget))

    def itemAt(self, index):
        if index < len(self._list):
            return self._list[index]

        return None

    def count(self):
        return len(self._list)

    def add(self, item):
        self._list.append(item)


class MissingItemAtLayout(QLayout):
    def __init__(self, parent=None):
        QLayout.__init__(self, parent)
        self._list = []

    def addItem(self, item):
        self.add(item)

    def addWidget(self, widget):
        self.add(QWidgetItem(widget))

    def count(self):
        return len(self._list)

    def add(self, item):
        self._list.append(item)

# Test if a layout implemented in python, the QWidget.setLayout works
# fine because this implement som layout functions used in glue code of
# QWidget, then in c++ when call a virtual function this need call the QLayout
# function implemented in python


class QLayoutTest(UsesQApplication):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testOwnershipTransfer(self):
        b = QPushButton("teste")
        l = MyLayout()

        l.addWidget(b)

        self.assertEqual(sys.getrefcount(b), 2)

        w = QWidget()

        # transfer ref
        w.setLayout(l)

        self.assertEqual(sys.getrefcount(b), 3)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReferenceTransfer(self):
        b = QPushButton("teste")
        l = QHBoxLayout()

        # keep ref
        l.addWidget(b)
        self.assertEqual(sys.getrefcount(b), 3)

        w = QWidget()

        # transfer ref
        w.setLayout(l)

        self.assertEqual(sys.getrefcount(b), 3)

        # release ref
        del w

        self.assertEqual(sys.getrefcount(b), 2)

    def testMissingFunctions(self):
        w = QWidget()
        b = QPushButton("test")
        l = MissingItemAtLayout()

        l.addWidget(b)

        self.assertRaises(RuntimeError, w.setLayout, l)

    def testQFormLayout(self):
        w = QWidget()
        formLayout = QFormLayout()
        spacer = QSpacerItem(100, 30)
        formLayout.setItem(0, QFormLayout.SpanningRole, spacer)
        w.setLayout(formLayout)
        w.show()
        QTimer.singleShot(10, w.close)
        self.app.exec()
        del w
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # PYSIDE-535: Why do I need to do it twice, here?
        gc.collect()
        self.assertRaises(RuntimeError, spacer.isEmpty)

    def testConstructorProperties(self):
        """PYSIDE-1986, test passing properties to the constructor of
           QHBoxLayout, which does not have default arguments."""
        layout = QHBoxLayout(objectName="layout", spacing=30)
        self.assertEqual(layout.spacing(), 30)
        self.assertEqual(layout.objectName(), "layout")


if __name__ == '__main__':
    unittest.main()
