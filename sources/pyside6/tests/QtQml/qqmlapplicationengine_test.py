# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for QQmlApplicationEngine'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.timedqguiapplication import TimedQGuiApplication

from PySide6.QtCore import QUrl, QObject, QTimer, Qt
from PySide6.QtQml import QQmlApplicationEngine


class TestQQmlApplicationEngine(TimedQGuiApplication):

    def testQQmlApplicationEngine(self):
        engine = QQmlApplicationEngine()

        qml_file_path = Path(__file__).resolve().parent / "qqmlapplicationengine.qml"

        # PYSIDE-1736: load from a string.
        engine.load(os.fspath(qml_file_path))
        rootObjects = engine.rootObjects()
        self.assertTrue(rootObjects)
        window = rootObjects[0]
        window.setTitle("TestQQmlApplicationEngine")
        QTimer.singleShot(100, window.close)


if __name__ == '__main__':
    unittest.main()
