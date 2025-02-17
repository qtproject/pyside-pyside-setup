#!/usr/bin/python
# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for QtSerialBus'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from PySide6.QtCore import QFile  # noqa: E402
from PySide6.QtSerialBus import QCanDbcFileParser  # noqa: E402


class QSerialBusTest(unittest.TestCase):
    def setUp(self):
        self.dbc_file = Path(__file__).parent / "test.dbc"

    def test_qfile_open(self):
        f = QFile(str(self.dbc_file))
        self.assertTrue(f.open(QFile.OpenModeFlag.ReadOnly), msg=f.errorString())
        f.close()

    def test_qcandbcfileparser_parse(self):
        parser = QCanDbcFileParser()

        self.assertTrue(parser.parse([str(self.dbc_file)]), msg=parser.errorString())

        self.assertTrue(parser.parse(str(self.dbc_file)), msg=parser.errorString())

        self.assertTrue(parser.parse([str(self.dbc_file.resolve())]), msg=parser.errorString())
        self.assertTrue(parser.parse(str(self.dbc_file.resolve())), msg=parser.errorString())

        self.assertFalse(parser.parse(["."]), msg=parser.errorString())


if __name__ == '__main__':
    unittest.main()
