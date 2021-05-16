#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# Copyright (C) 2011 Thomas Perl <m@thp.io>
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# Testcase for PySide bug 847
# Released under the same terms as PySide itself
# 2011-05-04 Thomas Perl <m@thp.io>

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.usesqapplication import UsesQApplication

from PySide6.QtCore import Slot, Signal, QUrl, QTimer, QCoreApplication
from PySide6.QtQuick import QQuickView


class View(QQuickView):
    def __init__(self):
        super().__init__()

    called = Signal(int, int)

    @Slot(int, int)
    def blubb(self, x, y):
        self.called.emit(x, y)


class TestQML(UsesQApplication):
    def done(self, x, y):
        self._sucess = True
        self.app.quit()
        print("done called")

    def testPythonSlot(self):
        self._sucess = False
        view = View()

        # Connect first, then set the property.
        view.called.connect(self.done)
        file = Path(__file__).resolve().parent / 'bug_847.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        while view.status() == QQuickView.Loading:
            self.app.processEvents()
        self.assertEqual(view.status(), QQuickView.Ready)
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.rootObject().setProperty('pythonObject', view)

        view.show()
        while not view.isExposed():
            self.app.processEvents()

        # Essentially a timeout in case method invocation fails.
        QTimer.singleShot(30000, QCoreApplication.instance().quit)
        self.app.exec()
        self.assertTrue(self._sucess)


if __name__ == '__main__':
    unittest.main()

