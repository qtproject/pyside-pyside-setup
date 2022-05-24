# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QTimer, QThread
from PySide6.QtWidgets import QTableView, QWidget


class Foo(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)


from helper.usesqapplication import UsesQApplication


class TestParentType(UsesQApplication):

    def testParentType(self):
        # Test the problem with calling QObject.parent from a QWidget
        # when the parent is a python class derived from a QWidget-derived
        # class. The method was returning the last C++ class in the hierarchy
        parent = Foo()
        w2 = QWidget(parent)
        self.assertTrue(isinstance(w2.parentWidget(), Foo))
        self.assertTrue(isinstance(w2.parent(), Foo))


if __name__ == '__main__':
    unittest.main()
