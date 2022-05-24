# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.timedqguiapplication import TimedQGuiApplication

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QObject, Signal, Slot, QUrl, QTimer, Property
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "test.Obj"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Obj(QObject):
    def __init__(self):
        super().__init__()
        self.value = 0

    sumResult = Signal(int, name="sumResult", arguments=['sum'])

    @Slot(int, int)
    def sum(self, arg1, arg2):
        self.sumResult.emit(arg1 + arg2)

    @Slot(str)
    def sendValue(self, s):
        self.value = int(s)


class TestConnectionWithQml(TimedQGuiApplication):

    def testSignalArguments(self):
        view = QQuickView()
        obj = Obj()

        view.setInitialProperties({"o": obj})
        file = Path(__file__).resolve().parent / 'signal_arguments.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        root = view.rootObject()
        self.assertTrue(root, quickview_errorstring(view))
        button = root.findChild(QObject, "button")
        self.assertTrue(button)
        view.show()
        button.clicked.emit()
        self.assertEqual(obj.value, 42)


if __name__ == '__main__':
    unittest.main()
