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

from PySide6.QtWidgets import QPushButton, QTabWidget
from helper.timedqapplication import TimedQApplication


def makeBug643(tab):
    button = QPushButton('Foo')
    tab.insertTab(0, button, 'Foo')


class RemoveTabMethod(TimedQApplication):
    def setUp(self):
        TimedQApplication.setUp(self)
        self.tab = QTabWidget()

    def tearDown(self):
        del self.tab
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        TimedQApplication.tearDown(self)

    def testRemoveTabPresence(self):
        self.assertTrue(getattr(self.tab, 'removeTab'))

    def testInsertTab(self):
        makeBug643(self.tab)
        self.assertEqual(self.tab.count(), 1)


if __name__ == '__main__':
    unittest.main()
