# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

''' unit test for BUG #1069 '''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QByteArray, QDataStream, QIODevice


class QDataStreamOpOverloadTestCase(unittest.TestCase):
    def setUp(self):
        self.ba = QByteArray()
        self.stream = QDataStream(self.ba, QIODevice.WriteOnly)

    def testIt(self):
        self.stream << "hello"
        ok = False
        for c in self.ba:
            if c != b'\x00':
                ok = True
                break

        self.assertEqual(ok, True)


if __name__ == "__main__":
    unittest.main()
