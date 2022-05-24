# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QDnsLookup'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication
from PySide6.QtNetwork import QDnsLookup


class DnsLookupTestCase(unittest.TestCase):
    '''Test case for QDnsLookup'''

    def setUp(self):
        self._app = QCoreApplication([])
        self._lookup = QDnsLookup(QDnsLookup.ANY, 'www.qt.io')
        self._lookup.finished.connect(self._finished)

    def tearDown(self):
        del self._lookup
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def _finished(self):
        if self._lookup.error() == QDnsLookup.NoError:
            nameRecords = self._lookup.canonicalNameRecords()
            if nameRecords:
                print(nameRecords[0].name())
        self._app.quit()

    def testLookup(self):
        self._lookup.lookup()
        self._app.exec()


if __name__ == '__main__':
    unittest.main()
