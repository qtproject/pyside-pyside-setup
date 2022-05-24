#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

""" PYSIDE-1755: https://bugreports.qt.io/projects/PYSIDE/issues/PYSIDE-1755
    Tests that a unittest.mock.MagicMock() can be used as a slot for quick
    prototyping. """

import os
import sys
import unittest
from unittest.mock import MagicMock

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject


class MockAsSlot(unittest.TestCase):
    def testMockAsSlot(self):
        obj = QObject()
        mock = MagicMock()
        obj.objectNameChanged.connect(mock)

        obj.objectNameChanged.emit("test")
        mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
