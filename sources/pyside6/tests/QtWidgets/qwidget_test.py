# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import sys
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QWidget, QMainWindow
from helper.usesqapplication import UsesQApplication


class QWidgetInherit(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)  # Intended: Initialize QWidget instead of base


class NativeEventTestWidget(QWidget):

    nativeEventCount = 0

    def __init__(self):
        super().__init__()

    def nativeEvent(self, eventType, message):
        self.nativeEventCount = self.nativeEventCount + 1
        return [False, 0]


class QWidgetTest(UsesQApplication):

    def testInheritance(self):
        self.assertRaises(TypeError, QWidgetInherit)


class QWidgetVisible(UsesQApplication):

    def testBasic(self):
        # Also related to bug #244, on existence of setVisible'''
        widget = NativeEventTestWidget()
        self.assertTrue(not widget.isVisible())
        widget.setVisible(True)
        self.assertTrue(widget.isVisible())
        self.assertTrue(widget.winId() != 0)
        # skip this test on macOS since no native events are received
        if sys.platform == 'darwin':
            return
        for i in range(10):
            if widget.nativeEventCount > 0:
                break
            self.app.processEvents()
        self.assertTrue(widget.nativeEventCount > 0)


if __name__ == '__main__':
    unittest.main()
