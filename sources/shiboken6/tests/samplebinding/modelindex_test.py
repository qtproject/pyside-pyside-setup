#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ModelIndex, ReferentModelIndex, PersistentModelIndex

class TestCastOperator(unittest.TestCase):

    def testCastOperatorReturningValue(self):
        index = PersistentModelIndex()
        index.setValue(123)
        self.assertEqual(index.value(), 123)
        self.assertEqual(index.value(), ModelIndex.getValue(index))

    def testCastOperatorReturningReference(self):
        index = ReferentModelIndex()
        index.setValue(123)
        self.assertEqual(index.value(), 123)
        self.assertEqual(index.value(), ModelIndex.getValue(index))


if __name__ == '__main__':
    unittest.main()

