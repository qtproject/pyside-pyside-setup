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
from PySide6.QtCore import QObject, QTimer, QUrl, Property, Slot
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "test.RotateValue"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class RotateValue(QObject):
    def __init__(self):
        super().__init__()

    @Slot(result=int)
    def val(self):
        return 100

    def setRotation(self, v):
        self._rotation = v

    def getRotation(self):
        return self._rotation

    rotation = Property(int, getRotation, setRotation)


class TestConnectionWithInvalidSignature(TimedQGuiApplication):

    def testSlotRetur(self):
        view = QQuickView()
        rotatevalue = RotateValue()

        timer = QTimer()
        timer.start(2000)

        view.setInitialProperties({"rotatevalue": rotatevalue})
        file = Path(__file__).resolve().parent / 'bug_456.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        root = view.rootObject()
        self.assertTrue(root, quickview_errorstring(view))
        button = root.findChild(QObject, "buttonMouseArea")
        view.show()
        button.entered.emit()
        self.assertEqual(rotatevalue.rotation, 100)


if __name__ == '__main__':
    unittest.main()
