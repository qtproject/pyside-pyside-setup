# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test paint event override in python'''

import gc
import os
import sys
import unittest

from textwrap import dedent

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget

from helper.usesqapplication import UsesQApplication


class MyWidget(QWidget):
    '''Sample widget'''

    def __init__(self, app):
        # Creates a new widget
        assert(app)

        super().__init__()
        self.app = app
        self.paint_event_called = False

    def paintEvent(self, event):
        # Empty paint event method
        super().paintEvent(event)
        self.paint_event_called = True
        QTimer.singleShot(20, self.close)


class PaintEventOverride(UsesQApplication):
    '''Test case for overriding QWidget.paintEvent'''

    qapplication = True

    def setUp(self):
        # Acquire resources
        super(PaintEventOverride, self).setUp()
        self.widget = MyWidget(self.app)

    def tearDown(self):
        # Release resources
        del self.widget
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(PaintEventOverride, self).tearDown()

    def testPaintEvent(self):
        # Test QWidget.paintEvent override
        self.widget.show()
        self.widget.setWindowTitle("paint_event_test")
        self.app.exec()
        self.assertTrue(self.widget.paint_event_called)


if __name__ == '__main__':
    unittest.main()
