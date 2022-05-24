# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QBuffer


class TestBug938 (unittest.TestCase):

    def testIt(self):
        b = QBuffer()
        b.open(QBuffer.WriteOnly)
        b.write(bytes("\x0023\x005", "UTF-8"))
        b.close()
        self.assertEqual(b.buffer().size(), 5)


if __name__ == '__main__':
    unittest.main()
