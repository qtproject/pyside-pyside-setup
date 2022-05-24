#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QUuid'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QUuid


class QUuidTest(unittest.TestCase):
    def testFromString(self):
        uuidString = '{fc69b59e-cc34-4436-a43c-ee95d128b8c5}'
#       testing overload QUUid::fromString(QStringView)
        uuid = QUuid.fromString(uuidString)
        self.assertTrue(not uuid.isNull())
        self.assertEqual(uuid.toString(), uuidString)


if __name__ == '__main__':
    unittest.main()
