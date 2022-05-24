# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for QMenuBar.addAction(identifier, callback) calls'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, SLOT
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QPushButton

from helper.usesqapplication import UsesQApplication


class AddActionTest(UsesQApplication):
    '''QMenuBar addAction'''

    def tearDown(self):
        try:
            del self.called
        except AttributeError:
            pass
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(AddActionTest, self).tearDown()

    def _callback(self):
        self.called = True

    def testBasic(self):
        '''QMenuBar.addAction(id, callback)'''
        menubar = QMenuBar()
        action = menubar.addAction("Accounts", self._callback)
        action.activate(QAction.Trigger)
        action.setShortcut(Qt.Key_A)
        self.assertTrue(self.called)

    def testWithCppSlot(self):
        '''QMenuBar.addAction(id, object, slot)'''
        menubar = QMenuBar()
        widget = QPushButton()
        widget.setCheckable(True)
        widget.setChecked(False)
        action = menubar.addAction("Accounts", widget, SLOT("toggle()"))
        action.setShortcut(Qt.Key_A)
        action.activate(QAction.Trigger)
        self.assertTrue(widget.isChecked())


if __name__ == '__main__':
    unittest.main()

