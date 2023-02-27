# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QPageRanges, Qt


class QTextDocumentFunctions(unittest.TestCase):

    def testFunctions(self):
        self.assertFalse(Qt.mightBeRichText('bla'))
        self.assertTrue(Qt.mightBeRichText('<html><head/><body><p>bla</p></body></html>'))
        html = Qt.convertFromPlainText("A & B", Qt.WhiteSpaceNormal)
        self.assertEqual(html, '<p>A &amp; B</p>')


class QPageRangesTest(unittest.TestCase):
    """PYSIDE-2237: Test that field QPageRanges.Range.from is properly mangled."""

    def test(self):
        pr = QPageRanges()
        pr.addPage(1)
        r0 = pr.toRangeList()[0]
        self.assertEqual(r0.from_, 1)
        self.assertEqual(r0.to, 1)


if __name__ == '__main__':
    unittest.main()
