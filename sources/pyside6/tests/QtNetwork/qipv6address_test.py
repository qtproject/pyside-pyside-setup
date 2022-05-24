# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QIPv6Address'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtNetwork import QIPv6Address


class QIPv6AddressGetItemTest(unittest.TestCase):
    def testLength(self):
        ip = QIPv6Address()
        self.assertEqual(len(ip), 16)

    def testSetItemNegativeIndex(self):
        ip = QIPv6Address()
        ip[-1] = 8
        self.assertEqual(ip[-1], 8)

    def testSetItemLargeIndex(self):
        ip = QIPv6Address()
        self.assertRaises(IndexError, ip.__setitem__, 32, 16)


if __name__ == '__main__':
    unittest.main()
