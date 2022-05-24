# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QInputDialog, QDialog
from helper.usesqapplication import UsesQApplication


def close_dialog():
    for w in QApplication.topLevelWidgets():
        if isinstance(w, QDialog):
            w.reject()


class TestInputDialog(UsesQApplication):

    def testGetDouble(self):
        QTimer.singleShot(500, close_dialog)
        self.assertEqual(QInputDialog.getDouble(None, "title", "label"), (0.0, False))

    def testGetInt(self):
        QTimer.singleShot(500, close_dialog)
        self.assertEqual(QInputDialog.getInt(None, "title", "label"), (0, False))

    def testGetItem(self):
        QTimer.singleShot(500, close_dialog)
        (item, bool) = QInputDialog.getItem(None, "title", "label", ["1", "2", "3"])
        self.assertEqual(str(item), "1")

    def testGetText(self):
        QTimer.singleShot(500, close_dialog)
        (text, bool) = QInputDialog.getText(None, "title", "label")
        self.assertEqual(str(text), "")


if __name__ == '__main__':
    unittest.main()

