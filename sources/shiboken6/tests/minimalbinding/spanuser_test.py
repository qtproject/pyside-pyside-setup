#!/usr/bin/env python
# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from minimal import SpanUser


class IntSpanTest(unittest.TestCase):

    def testCreateIntSpan(self):
        if not SpanUser.enabled():
            return
        expected = [1, 2, 3]
        self.assertEqual(SpanUser.getIntSpan3(), expected)
        self.assertEqual(SpanUser.getIntSpan(), expected)
        self.assertEqual(SpanUser.getConstIntSpan3(), expected)

        self.assertEqual(SpanUser.sumIntSpan3(expected), 6)
        self.assertEqual(SpanUser.sumIntSpan(expected), 6)
        self.assertEqual(SpanUser.sumConstIntSpan3(expected), 6)

    def testSpanOpaqueContainer(self):
        if not SpanUser.enabled():
            return
        oc = SpanUser.getIntSpan3_OpaqueContainer()  # 1,2,3
        oc[1] = 10
        oc = SpanUser.getIntSpan3_OpaqueContainer()
        # note: This converts to std::vector
        self.assertEqual(SpanUser.sumIntSpan3(oc), 14)


if __name__ == '__main__':
    unittest.main()
