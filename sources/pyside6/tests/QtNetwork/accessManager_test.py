# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QHttp'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from helper.usesqapplication import UsesQApplication
from httpd import TestServer


class AccessManagerCase(UsesQApplication):

    def setUp(self):
        super(AccessManagerCase, self).setUp()
        self.httpd = TestServer()
        self.httpd.start()
        self.called = False

    def tearDown(self):
        super(AccessManagerCase, self).tearDown()
        if self.httpd:
            self.httpd.shutdown()
            self.httpd = None

    def goAway(self):
        self.httpd.shutdown()
        self.app.quit()
        self.httpd = None

    def slot_replyFinished(self, reply):
        self.assertEqual(type(reply), QNetworkReply)
        self.called = True
        self.goAway()

    def testNetworkRequest(self):
        manager = QNetworkAccessManager()
        manager.finished.connect(self.slot_replyFinished)
        port = self.httpd.port()
        manager.get(QNetworkRequest(QUrl(f"http://127.0.0.1:{port}")))
        self.app.exec()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
