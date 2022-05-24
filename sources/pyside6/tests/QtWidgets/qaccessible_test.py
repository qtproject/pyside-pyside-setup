# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QAccessible::installFactory().'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QAccessible, QAccessibleInterface, QColor
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout

from helper.usesqapplication import UsesQApplication


class LineEditAccessible(QAccessibleInterface):
    """Mimick a QAccessibleInterface implementation for QLineEdit."""

    instance_count = 0

    def __init__(self, widget):
        super().__init__()
        LineEditAccessible.instance_count += 1
        self._widget = widget
        self._name = self._widget.objectName()
        print('LineEditAccessible', self._name)

    def __del__(self):
        LineEditAccessible.instance_count -= 1
        print('~LineEditAccessible', self._name)

    def actionInterface(self):
        return None

    def backgroundColor(self):
        return QColor(Qt.white)

    def child(self, index):
        return None

    def childAt(self, x, y):
        return None

    def childCount(self):
        return 0

    def focusChild(self):
        return None

    def foregroundColor(self):
        return QColor(Qt.black)

    def indexOfChild(self, child):
        return -1

    def isValid(self):
        return True

    def object(self):
        return self._widget

    def parent(self):
        return None

    def rect(self):
        return self._widget.geometry()

    def role(self):
        return QAccessible.EditableText

    def setText(self, t, text):
        pass

    def state(self):
        return QAccessible.State()

    def tableCellInterface(self):
        return None

    def tableInterface(self):
        return None

    def text(self, t):
        return self._widget.text() if t == QAccessible.Value else ''

    def textInterface(self):
        return None

    def valueInterface(self):
        return None

    def window(self):
        return self._widget.window().windowHandle()


def accessible_factory(key, obj):
    """Factory function for QAccessibleInterface for QLineEdit's."""
    if obj.metaObject().className() == 'QLineEdit':
        return LineEditAccessible(obj)
    return None


class Window(QWidget):
    """Test window with 2 QLineEdit's."""
    def __init__(self):
        super().__init__()
        self.setObjectName('top')
        layout = QVBoxLayout(self)
        self.m_line_edit1 = QLineEdit("bla")
        layout.addWidget(self.m_line_edit1)
        self.m_line_edit2 = QLineEdit("bla")
        layout.addWidget(self.m_line_edit2)


class QAccessibleTest(UsesQApplication):
    """Test that LineEditAccessible instances are created for QLineEdit's."""

    def setUp(self):
        super().setUp()
        QAccessible.installFactory(accessible_factory)
        window = Window()

    def testLineEdits(self):
        window = Window()
        window.show()
        while not window.windowHandle().isExposed():
            QCoreApplication.processEvents()
        self.assertEqual(LineEditAccessible.instance_count, 2)


if __name__ == "__main__":
    unittest.main()
