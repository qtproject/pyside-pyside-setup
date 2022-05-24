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

from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QKeySequence, QIcon
from PySide6.QtCore import SLOT

from helper.usesqapplication import UsesQApplication


class QMenuAddAction(UsesQApplication):

    def setUp(self):
        super(QMenuAddAction, self).setUp()
        self.menu = QMenu()

    def tearDown(self):
        del self.menu
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(QMenuAddAction, self).tearDown()

    def testAddActionWithoutKeySequenceCallable(self):
        # bug #280
        action = self.menu.addAction(self.app.tr('aaa'), lambda: 1)

    def testAddActionKeySequenceCallable(self):
        # bug #228
        action = self.menu.addAction(self.app.tr('aaa'), lambda: 1,
                                    QKeySequence(self.app.tr('Ctrl+O')))

    def testAddActionKeySequenceSlot(self):
        action = self.menu.addAction('Quit', self.app, SLOT('quit()'),
                                    QKeySequence('Ctrl+O'))


class QMenuAddActionWithIcon(UsesQApplication):

    def setUp(self):
        super(QMenuAddActionWithIcon, self).setUp()
        self.menu = QMenu()
        self.icon = QIcon()

    def tearDown(self):
        del self.menu
        del self.icon
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(QMenuAddActionWithIcon, self).tearDown()

    def testAddActionWithoutKeySequenceCallable(self):
        # bug #280
        action = self.menu.addAction(self.icon, self.app.tr('aaa'), lambda: 1)

    def testAddActionKeySequenceCallable(self):
        # bug #228
        action = self.menu.addAction(self.icon, self.app.tr('aaa'), lambda: 1,
                                    QKeySequence(self.app.tr('Ctrl+O')))

    def testAddActionKeySequenceSlot(self):
        action = self.menu.addAction(self.icon, 'Quit', self.app, SLOT('quit()'),
                                    QKeySequence('Ctrl+O'))


if __name__ == '__main__':
    unittest.main()
