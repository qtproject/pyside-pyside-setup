#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QFile, QFileInfo, QDir
from PySide6.QtWidgets import QApplication
from PySide6.QtSvgWidgets import QSvgWidget


class QSvgWidgetTest(unittest.TestCase):

    def testLoad(self):
        directory = os.path.dirname(__file__)
        tigerPath = QDir.cleanPath(f"{directory}/../QtSvg/tiger.svg")
        self.assertTrue(QFileInfo.exists(tigerPath))

        app = QApplication([])
        fromFile = QSvgWidget()
        fromFile.load(tigerPath)
        self.assertTrue(fromFile.renderer().isValid())

        tigerFile = QFile(tigerPath)
        tigerFile.open(QFile.ReadOnly)
        tigerData = tigerFile.readAll()
        fromContents = QSvgWidget()
        fromContents.load(tigerData)
        self.assertTrue(fromContents.renderer().isValid())


if __name__ == '__main__':
    unittest.main()

