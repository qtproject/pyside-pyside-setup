# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests for QKeyEvent'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLineEdit
from PySide6.QtTest import QTest

from helper.usesqapplication import UsesQApplication


class KeyEventFilter(QObject):

    def __init__(self, widget, eventType, key):
        super().__init__()

        self.widget = widget
        self.eventType = eventType
        self.key = key

        self.processed = False

    def eventFilter(self, obj, event):
        if self.widget == obj and event.type() == self.eventType and \
               isinstance(event, QKeyEvent) and event.key() == self.key:
            self.processed = True
            return True

        return False


class EventFilterTest(UsesQApplication):

    def testKeyEvent(self):
        widget = QLineEdit()
        key = Qt.Key_A
        eventFilter = KeyEventFilter(widget, QEvent.KeyPress, key)
        widget.installEventFilter(eventFilter)

        QTest.keyClick(widget, key)

        self.assertTrue(eventFilter.processed)


if __name__ == '__main__':
    unittest.main()
