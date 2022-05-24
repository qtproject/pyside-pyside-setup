# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QToolbar'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QMainWindow

from helper.usesqapplication import UsesQApplication


class AddActionText(UsesQApplication):
    '''Test case for calling QToolbar.addAction passing a text'''

    def setUp(self):
        # Acquire resources
        super(AddActionText, self).setUp()
        self.window = QMainWindow()
        self.toolbar = QToolBar()
        self.window.addToolBar(self.toolbar)

    def tearDown(self):
        # Release resources
        super(AddActionText, self).tearDown()
        del self.toolbar
        del self.window
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testText(self):
        # QToolBar.addAction(text) - add a QToolButton
        self.toolbar.addAction('aaaa')
        self.assertEqual(len(self.toolbar.actions()), 1)
        action = self.toolbar.actions()[0]
        self.assertTrue(isinstance(action, QAction))
        self.assertEqual(action.text(), 'aaaa')


if __name__ == '__main__':
    unittest.main()
