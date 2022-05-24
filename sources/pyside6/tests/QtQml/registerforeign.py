# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import qmlcomponent_errorstring
from helper.timedqguiapplication import TimedQGuiApplication

from PySide6.QtCore import Property, QObject, QUrl, qVersion
from PySide6.QtGui import QGuiApplication, QRasterWindow
from PySide6.QtQml import (QmlNamedElement, QmlForeign, QQmlEngine,
                           QQmlComponent)


"""Test the QmlForeign decorator, letting the QQmlEngine create a QRasterWindow."""


QML_IMPORT_NAME = "Foreign"
QML_IMPORT_MAJOR_VERSION = 1


@QmlNamedElement("QRasterWindow")
@QmlForeign(QRasterWindow)
class RasterWindowForeign(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)


class TestQmlForeign(TimedQGuiApplication):

    def testIt(self):
        engine = QQmlEngine()
        file = Path(__file__).resolve().parent / 'registerforeign.qml'
        self.assertTrue(file.is_file())
        component = QQmlComponent(engine, QUrl.fromLocalFile(file))
        window = component.create()
        self.assertTrue(window, qmlcomponent_errorstring(component))
        self.assertEqual(type(window), QRasterWindow)
        window.setTitle(f"Qt {qVersion()}")
        window.show()
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
