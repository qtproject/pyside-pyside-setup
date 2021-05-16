# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtNetwork import QHostAddress, QTcpServer, QTcpSocket
from helper.usesqapplication import UsesQApplication


class HttpSignalsCase(UsesQApplication):
    '''Test case for launching QHttp signals'''
    DATA = bytes("PySide rocks", "UTF-8")

    def onError(self):
        self.assertTrue(False)

    def onNewConnection(self):
        self.serverConnection = self.server.nextPendingConnection()
        self.serverConnection.errorOccurred.connect(self.onError)
        self.serverConnection.write(HttpSignalsCase.DATA)
        self.server.close()

    def onReadReady(self):
        data = self.client.read(100)
        self.assertEqual(len(data), len(HttpSignalsCase.DATA))
        self.assertEqual(data, HttpSignalsCase.DATA)
        self.done()

    def onClientConnect(self):
        self.client.readyRead.connect(self.onReadReady)

    def initServer(self):
        self.server = QTcpServer()
        self.server.newConnection.connect(self.onNewConnection)
        self.assertTrue(self.server.listen())
        self.client = QTcpSocket()
        self.client.connected.connect(self.onClientConnect)
        self.client.connectToHost(QHostAddress(QHostAddress.LocalHost), self.server.serverPort())

    def done(self):
        self.serverConnection.close()
        self.client.close()
        self.app.quit()

    def testRun(self):
        self.initServer()
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
