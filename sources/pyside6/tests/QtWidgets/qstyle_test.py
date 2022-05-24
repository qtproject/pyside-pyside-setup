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

from helper.usesqapplication import UsesQApplication

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import (QApplication, QFontComboBox, QLabel, QProxyStyle,
    QStyleFactory, QWidget)


class ProxyStyle(QProxyStyle):

    def __init__(self, style):
        QProxyStyle.__init__(self, style)
        self.polished = 0

    def polish(self, widget):
        self.polished = self.polished + 1
        super(ProxyStyle, self).polish(widget)


class SetStyleTest(UsesQApplication):
    '''Tests setting the same QStyle for all objects in a UI hierarchy.'''

    def testSetStyle(self):
        '''All this test have to do is not break with some invalid Python wrapper.'''

        def setStyleHelper(widget, style):
            widget.setStyle(style)
            widget.setPalette(style.standardPalette())
            for child in widget.children():
                if isinstance(child, QWidget):
                    setStyleHelper(child, style)

        container = QWidget()
        # QFontComboBox is used because it has an QLineEdit created in C++ inside it,
        # and if the QWidget.setStyle(style) steals the ownership of the style
        # for the C++ originated widget everything will break.
        fontComboBox = QFontComboBox(container)
        label = QLabel(container)
        label.setText('Label')
        style = QStyleFactory.create(QStyleFactory.keys()[0])
        setStyleHelper(container, style)

    def testSetProxyStyle(self):
        label = QLabel("QtWidgets/ProxyStyle test")
        baseStyle = QStyleFactory.create(QApplication.instance().style().objectName())
        self.assertTrue(baseStyle)
        proxyStyle = ProxyStyle(baseStyle)
        label.setStyle(proxyStyle)
        label.show()
        while not label.windowHandle().isExposed():
            QApplication.instance().processEvents()
        self.assertTrue(proxyStyle.polished > 0)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testSetStyleOwnership(self):
        style = QStyleFactory.create(QStyleFactory.keys()[0])
        self.assertEqual(sys.getrefcount(style), 2)
        QApplication.instance().setStyle(style)
        self.assertEqual(sys.getrefcount(style), 3)


if __name__ == '__main__':
    unittest.main()

