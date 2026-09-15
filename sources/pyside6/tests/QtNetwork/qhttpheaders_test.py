# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for QHttpHeaders'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtNetwork import QHttpHeaders, QHttpHeaderRangeSet


class QHttpHeadersTest(unittest.TestCase):
    '''Test case for QHttpHeaders.'''

    def testRange(self):
        hs = QHttpHeaderRangeSet()
        r = [(1, 2), (3, 4), (5, None)]
        hs.setRanges(r)
        h = QHttpHeaders()
        h.setRangeValues(hs)
        self.assertEqual(h.rangeValues().ranges(), r)


if __name__ == '__main__':
    unittest.main()
