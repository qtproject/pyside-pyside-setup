#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QUuid'''

import os
import socket
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QSocketNotifier


class QSocketNotifierTest(unittest.TestCase):
    def testClass(self):
        app = QCoreApplication([])
        # socketpair is not available on Windows
        if os.name != "nt":
            w_sock, r_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)

            self.assertIsInstance(r_sock.fileno(), int)

            notifier = QSocketNotifier(r_sock.fileno(), QSocketNotifier.Read)

            self.assertIsNotNone(notifier)

            w_sock.close()
            r_sock.close()


if __name__ == '__main__':
    unittest.main()
