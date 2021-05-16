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
from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QCoreApplication, QTimer, QUrl, Slot
from PySide6.QtQml import QQmlPropertyMap
from PySide6.QtQuick import QQuickView


class TestBug(UsesQApplication):

    def setUp(self):
        super().setUp()
        self._complete = False

    @Slot()
    def complete(self):
        self._complete = True
        self.app.quit()

    def testQMLFunctionCall(self):
        ownerData = QQmlPropertyMap()
        ownerData.insert('name', 'John Smith')
        ownerData.insert('phone', '555-5555')
        ownerData.insert('newValue', '')

        self._view = QQuickView()
        self._view.engine().quit.connect(self.complete)
        self._view.setInitialProperties({'owner': ownerData})
        file = Path(__file__).resolve().parent / 'bug_997.qml'
        self.assertTrue(file.is_file())
        self._view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(self._view.rootObject(), quickview_errorstring(self._view))
        self._view.show()
        if not self._complete:
            self.app.exec()
        self.assertEqual(ownerData.value('newName'), ownerData.value('name'))


if __name__ == '__main__':
    unittest.main()
