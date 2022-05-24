#!/usr/bin/python
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

from helper.helper import quickview_errorstring

from PySide6.QtCore import QObject, QUrl, Slot, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlIncubationController, VolatileBool
from PySide6.QtQuick import QQuickView


class CustomIncubationController(QObject, QQmlIncubationController):
    def __init__(self, test):
        QObject.__init__(self)
        QQmlIncubationController.__init__(self)
        self.test = test
        self.interrupted = False

        # Incubate every 50 milliseconds
        self.startTimer(50)
        self.incubationShouldContinue = VolatileBool(True)
        self.test.assertEqual(self.incubationShouldContinue.get(), True)

    @Slot()
    def interrupter(self):
        if not self.interrupted:
            self.interrupted = True
            self.incubationShouldContinue.set(False)
            self.test.assertEqual(self.incubationShouldContinue.get(), False)
            QTimer.singleShot(0, QGuiApplication.instance().quit)

    def timerEvent(self, ev):
        # Incubate items for 2000 milliseconds, or until the volatile bool is set to false.
        self.incubateWhile(self.incubationShouldContinue, 2000)


class TestBug(unittest.TestCase):
    def testIncubateWhileCall(self):
        app = QGuiApplication(sys.argv)
        view = QQuickView()
        controller = CustomIncubationController(self)
        view.engine().setIncubationController(controller)
        view.setResizeMode(QQuickView.SizeRootObjectToView)
        file = Path(__file__).resolve().parent / 'qqmlincubator_incubateWhile.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()

        root = view.rootObject()
        # The QML code will issue an interrupt signal after half of its items are loaded.
        root.shouldInterrupt.connect(controller.interrupter)
        res = app.exec()

        itemsToCreate = root.property("itemsToCreate")
        loadedItems = root.property("loadedItems")
        self.assertEqual(loadedItems, itemsToCreate / 2)

        # Finish incubating the remaining items.
        controller.incubateFor(1000)
        loadedItems = root.property("loadedItems")
        self.assertEqual(loadedItems, itemsToCreate)

        # Deleting the view before it goes out of scope is required to make sure all child QML
        # instances are destroyed in the correct order.
        del view
        del app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()


if __name__ == '__main__':
    unittest.main()
