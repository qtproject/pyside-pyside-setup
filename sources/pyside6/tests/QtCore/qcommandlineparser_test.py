#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QCommandLineParser and QCommandLineOption'''

import ctypes
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QCommandLineOption, QCommandLineParser


class QCommandLineParserTest(unittest.TestCase):
    def testParser(self):
        app = QCoreApplication([])

        parser1 = QCommandLineParser()
        self.assertEqual(parser1.parse(["QtCore_qcommandlineparser_test", "file.txt"]), True)
        self.assertEqual(parser1.positionalArguments(), ["file.txt"])

        parser2 = QCommandLineParser()
        self.assertEqual(parser2.addOption(QCommandLineOption("b")), True)
        self.assertEqual(parser2.parse(["QtCore_qcommandlineparser_test", "-b"]), True)
        self.assertEqual(parser2.optionNames(), ["b"])
        self.assertEqual(parser2.isSet("b"), True)
        self.assertEqual(parser2.values("b"), [])
        self.assertEqual(parser2.positionalArguments(), [])


if __name__ == '__main__':
    unittest.main()
