# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''
Test case for bug #442

archive:
https://srinikom.github.io/pyside-bz-archive/442.html
'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.timedqguiapplication import TimedQGuiApplication
from PySide6.QtCore import QObject, QUrl, SIGNAL
from PySide6.QtGui import QColor
from PySide6.QtQuick import QQuickItem, QQuickView


class TestConnectionWithInvalidSignature(TimedQGuiApplication):
    def onButtonClicked(self):
        self.buttonClicked = True
        self.app.quit()

    def onButtonFailClicked(self):
        pass

    def testFailConnection(self):
        self.buttonClicked = False
        self.buttonFailClicked = False
        view = QQuickView()
        file = Path(__file__).resolve().parent / 'connect_python_qml.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        root = view.rootObject()
        self.assertTrue(root, quickview_errorstring(view))
        button = root.findChild(QObject, "buttonMouseArea")
        self.assertRaises(TypeError, QObject.connect, [button,SIGNAL('entered()'), self.onButtonFailClicked])
        button.entered.connect(self.onButtonClicked)
        button.entered.emit()
        view.show()
        self.app.exec()
        self.assertTrue(self.buttonClicked)


if __name__ == '__main__':
    unittest.main()
