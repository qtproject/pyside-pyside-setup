# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' unit test for BUG #1063 '''

import os
import sys
import tempfile
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QFile, QIODevice, QTextStream


class QTextStreamTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.f = QFile(self.temp_file.name)
        self.f.open(QIODevice.WriteOnly)
        self.strings = ('foo', 'bar')
        self.stream = QTextStream(self.f)

    def testIt(self):
        for s in self.strings:
            self.stream << s

        self.f.close()

        # make sure we didn't get an empty file
        self.assertNotEqual(QFile(self.temp_file.name).size(), 0)

        os.unlink(self.temp_file.name)


if __name__ == "__main__":
    unittest.main()
