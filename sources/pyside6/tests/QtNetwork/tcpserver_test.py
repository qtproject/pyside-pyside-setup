# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QTCPServer'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtNetwork import QTcpServer


class ListenDefaultArgsCase(unittest.TestCase):
    '''Test case for TcpServer.listen with default args'''

    def setUp(self):
        # Acquire resources
        self.server = QTcpServer()

    def tearDown(self):
        # Release resources
        del self.server
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testDefaultArgs(self):
        # @bug 108
        # Default arguments for QTcpServer.listen
        self.server.listen()


if __name__ == '__main__':
    unittest.main()
