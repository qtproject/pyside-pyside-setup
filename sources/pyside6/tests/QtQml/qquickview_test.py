# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QQuickView'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.timedqguiapplication import TimedQGuiApplication

from PySide6.QtCore import QUrl, QObject, Property, Slot, Signal
from PySide6.QtQml import QQmlEngine, QQmlContext
from PySide6.QtQuick import QQuickView


class MyObject(QObject):
    titleChanged = Signal()
    def __init__(self, text, parent=None):
        QObject.__init__(self, parent)
        self._text = text

    def getText(self):
        return self._text

    @Slot(str)
    def qmlText(self, text):
        self._qmlText = text

    title = Property(str, getText, notify=titleChanged)


class TestQQuickView(TimedQGuiApplication):

    def testQQuickViewList(self):
        view = QQuickView()

        dataList = ["Item 1", "Item 2", "Item 3", "Item 4"]

        view.setInitialProperties({"model": dataList})

        file = Path(__file__).resolve().parent / 'view.qml'
        self.assertTrue(file.is_file())
        url = QUrl.fromLocalFile(file)
        view.setSource(url)
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()

        self.assertEqual(view.status(), QQuickView.Ready)
        rootObject = view.rootObject()
        self.assertTrue(rootObject)
        context = QQmlEngine.contextForObject(rootObject)
        self.assertTrue(context)
        self.assertTrue(context.engine())

        test_context = QQmlContext(context)  # Context properties, PYSIDE-1921
        prop_pair = QQmlContext.PropertyPair()
        prop_pair.name = "testProperty"
        prop_pair.value = 42
        test_context.setContextProperties([prop_pair])
        self.assertTrue(test_context.contextProperty("testProperty"), 42)

    def testModelExport(self):
        view = QQuickView()
        dataList = [MyObject("Item 1"), MyObject("Item 2"), MyObject("Item 3"), MyObject("Item 4")]

        view.setInitialProperties({"model": dataList})

        file = Path(__file__).resolve().parent / 'viewmodel.qml'
        self.assertTrue(file.is_file())
        url = QUrl.fromLocalFile(file)
        view.setSource(url)
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()

        self.assertEqual(view.status(), QQuickView.Ready)


if __name__ == '__main__':
    unittest.main()
