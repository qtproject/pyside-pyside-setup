# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QUdpSocket'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUrl, QObject, SIGNAL, QCoreApplication, QTimer
from PySide6.QtNetwork import QUdpSocket, QHostAddress


class HttpSignalsCase(unittest.TestCase):
    '''Test case for bug #124 - readDatagram signature

    QUdpSocket.readDatagram must return a tuple with the datagram, host and
    port, while receiving only the max payload size.'''

    def setUp(self):
        # Acquire resources
        self.called = False
        self.app = QCoreApplication([])

        self.socket = QUdpSocket()

        self.server = QUdpSocket()
        self.server.bind(QHostAddress(QHostAddress.LocalHost), 45454)

    def tearDown(self):
        # Release resources
        del self.socket
        del self.server
        del self.app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def sendPackage(self):
        addr = QHostAddress(QHostAddress.LocalHost)
        self.socket.writeDatagram(bytes('datagram', "UTF-8"), addr, 45454)

    def callback(self):
        while self.server.hasPendingDatagrams():
            datagram, host, port = self.server.readDatagram(self.server.pendingDatagramSize())
            self.called = True
            self.app.quit()

    def testDefaultArgs(self):
        # QUdpSocket.readDatagram pythonic return
        # @bug 124
        self.server.readyRead.connect(self.callback)
        self.sendPackage()
        self.app.exec()

        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
