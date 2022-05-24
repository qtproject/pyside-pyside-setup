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

from PySide6.QtCore import QUrl
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickItem, QQuickView


class MyItem(QQuickItem):
    COMPONENT_COMPLETE_CALLED = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("myitem")

    def componentComplete(self):
        MyItem.COMPONENT_COMPLETE_CALLED = True
        super(MyItem, self).componentComplete()


class TestRegisterQMLType(TimedQGuiApplication):
    def setup(self):
        super.setup(100 * 3)  # 3s

    def testSignalEmission(self):
        qmlRegisterType(MyItem, "my.item", 1, 0, "MyItem")

        view = QQuickView()
        file = Path(__file__).resolve().parent / 'bug_951.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))

        self.app.exec()
        self.assertTrue(MyItem.COMPONENT_COMPLETE_CALLED)


if __name__ == '__main__':
    unittest.main()
