#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QRegularExpression'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QRegularExpression, QRegularExpressionMatch, QRegularExpressionMatchIterator


class QRegularExpressionTest(unittest.TestCase):

    def testMatch(self):
        re = QRegularExpression('^.*(word2).*$')
        self.assertTrue(re.isValid())
        match = re.match('word1 word2  word3')
        self.assertTrue(match.isValid())
        self.assertEqual(match.captured(1), 'word2')
        self.assertEqual(match.capturedView(1), 'word2')

    def testMatchIterator(self):
        re = QRegularExpression('(\w+)')
        self.assertTrue(re.isValid())
        count = 0
        it = re.globalMatch('word1 word2 word3')
        while it.hasNext():
            it.next()
            count = count + 1
        self.assertEqual(count, 3)


if __name__ == '__main__':
    unittest.main()
