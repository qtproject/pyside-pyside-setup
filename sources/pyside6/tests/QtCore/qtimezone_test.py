# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimeZone


class TestQTimeZone (unittest.TestCase):
    def testTimeZone(self):
        id = bytes('Europe/Berlin', "UTF-8")
        timeZone = QTimeZone(id)
        self.assertTrue(timeZone.isValid())
        self.assertEqual(timeZone.id(), id)
        name = timeZone.displayName(QTimeZone.GenericTime, QTimeZone.DefaultName)
        self.assertTrue(name)


if __name__ == '__main__':
    unittest.main()
