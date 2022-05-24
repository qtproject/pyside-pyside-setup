# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QQmlNetwork'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QGuiApplication, QWindow
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QQmlNetworkAccessManagerFactory
from PySide6.QtNetwork import QNetworkAccessManager

from helper.helper import quickview_errorstring
from helper.timedqguiapplication import TimedQGuiApplication


request_created = False


def check_done():
    global request_created
    if request_created:
        windows = QGuiApplication.topLevelWindows()
        if windows:
            windows[0].close()


class CustomManager(QNetworkAccessManager):
    """CustomManager (running in a different thread)"""
    def createRequest(self, op, req, data=None):
        global request_created
        print(">> createRequest ", self, op, req.url(), data)
        request_created = True
        return QNetworkAccessManager.createRequest(self, op, req, data)


class CustomFactory(QQmlNetworkAccessManagerFactory):
    def create(self, parent=None):
        return CustomManager()


class TestQQmlNetworkFactory(TimedQGuiApplication):
    def setUp(self):
        super().setUp(timeout=2000)

    def testQQuickNetworkFactory(self):
        view = QQuickView()
        self.factory = CustomFactory()
        view.engine().setNetworkAccessManagerFactory(self.factory)

        file = Path(__file__).resolve().parent / 'hw.qml'
        self.assertTrue(file.is_file())
        url = QUrl.fromLocalFile(file)

        view.setSource(url)
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()

        self.assertEqual(view.status(), QQuickView.Ready)

        timer = QTimer()
        timer.timeout.connect(check_done)
        timer.start(50)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
