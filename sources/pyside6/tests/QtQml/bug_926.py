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

from helper.helper import quickview_errorstring

from PySide6.QtCore import QUrl, QTimer, QObject, Signal, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickView


class MyClass (QObject):

    def __init__(self):
        super().__init__()
        self.__url = QUrl()

    def getUrl(self):
        return self.__url

    def setUrl(self, value):
        newUrl = QUrl(value)
        if (newUrl != self.__url):
            self.__url = newUrl
            self.urlChanged.emit()

    urlChanged = Signal()
    urla = Property(QUrl, getUrl, setUrl, notify=urlChanged)


class TestBug926 (unittest.TestCase):
    def testIt(self):
        app = QGuiApplication([])
        qmlRegisterType(MyClass,'Example', 1, 0, 'MyClass')
        view = QQuickView()
        file = Path(__file__).resolve().parent / 'bug_926.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))

        view.show()
        QTimer.singleShot(0, app.quit)
        app.exec()


if __name__ == '__main__':
    unittest.main()
