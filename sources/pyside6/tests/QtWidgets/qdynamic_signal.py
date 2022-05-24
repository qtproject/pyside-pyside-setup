# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QInputDialog

from helper.usesqapplication import UsesQApplication


class DynamicSignalTest(UsesQApplication):

    def cb(self, obj):
        self._called = True

    def testQDialog(self):
        dlg = QInputDialog()
        dlg.setInputMode(QInputDialog.TextInput)
        lst = dlg.children()
        self.assertTrue(len(lst))
        obj = lst[0]
        self._called = False
        obj.destroyed[QObject].connect(self.cb)
        obj = None
        del dlg
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self._called)


if __name__ == '__main__':
    unittest.main()
