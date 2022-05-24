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
from PySide6.QtWidgets import QSlider
from helper.usesqapplication import UsesQApplication


class TestBugPYSIDE189(UsesQApplication):

    def testDisconnect(self):
        # Disconnecting from a signal owned by a destroyed object
        # should raise an exception, not segfault.
        def onValueChanged(self, value):
            pass

        sld = QSlider()
        sld.valueChanged.connect(onValueChanged)

        sld.deleteLater()

        QTimer.singleShot(0, self.app.quit)
        self.app.exec()

        self.assertRaises(RuntimeError, sld.valueChanged.disconnect, onValueChanged)


if __name__ == '__main__':
    unittest.main()
