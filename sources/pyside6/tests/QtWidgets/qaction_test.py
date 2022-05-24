# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QMenu
from helper.usesqapplication import UsesQApplication


class QPainterDrawText(UsesQApplication):

    def _cb(self):
        self._called = True

    def testSignal(self):
        o = QWidget()
        act = QAction(o)
        self._called = False
        act.triggered.connect(self._cb)
        act.trigger()
        self.assertTrue(self._called)

    def testNewCtor(self):
        o = QWidget()
        self._called = False
        myAction = QAction("&Quit", o, triggered=self._cb)
        myAction.trigger()
        self.assertTrue(self._called)


class SetShortcutTest(UsesQApplication):

    def testSetShortcut(self):
        # Somehow an exception was leaking from the constructor
        # and appearing in setShortcut.
        o = QWidget()
        action = QAction('aaaa', o)
        shortcut = 'Ctrl+N'
        action.setShortcut(shortcut)
        s2 = action.shortcut()
        self.assertEqual(s2, shortcut)

    def testMenu(self):
        # Test the setMenu()/menu() old functionality removed in Qt6
        # that was added via helper functions.
        menu = QMenu("menu")
        action = QAction("action")

        # Using QAction::setMenu(QObject*)
        action.setMenu(menu)

        self.assertEqual(action.menu(), menu)


if __name__ == '__main__':
    unittest.main()

