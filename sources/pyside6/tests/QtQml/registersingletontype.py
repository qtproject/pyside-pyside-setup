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

from PySide6.QtCore import Property, Signal, QTimer, QUrl, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import (qmlRegisterSingletonType, qmlRegisterSingletonInstance,
                           QmlElement, QmlSingleton)
from PySide6.QtQuick import QQuickView

finalResult = 0


class SingletonQObject(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._data = 100

    def getData(self):
        return self._data

    def setData(self, data):
        global finalResult
        finalResult = self._data = data

    data = Property(int, getData, setData)


def singletonQObjectCallback(engine):
    obj = SingletonQObject()
    obj.setData(50)
    return obj


def singletonQJSValueCallback(engine):
    return engine.evaluate("new Object({data: 50})")


QML_IMPORT_NAME = "Singletons"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
@QmlSingleton
class DecoratedSingletonQObject(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = 200

    def getData(self):
        return self._data

    def setData(self, data):
        self._data = data

    data = Property(int, getData, setData)


class TestQmlSupport(unittest.TestCase):
    def testIt(self):
        app = QGuiApplication([])

        qmlRegisterSingletonType(SingletonQObject, 'Singletons', 1, 0, 'SingletonQObjectNoCallback')
        qmlRegisterSingletonType(SingletonQObject, 'Singletons', 1, 0, 'SingletonQObjectCallback',
                                 singletonQObjectCallback)

        qmlRegisterSingletonType('Singletons', 1, 0, 'SingletonQJSValue', singletonQJSValueCallback)

        # Accepts only QObject derived types
        l = [1, 2]
        with self.assertRaises(TypeError):
            qmlRegisterSingletonInstance(SingletonQObject, 'Singletons', 1, 0, 'SingletonInstance', l)

        # Modify value on the instance
        s = SingletonQObject()
        s.setData(99)
        qmlRegisterSingletonInstance(SingletonQObject, 'Singletons', 1, 0, 'SingletonInstance', s)

        view = QQuickView()
        file = Path(__file__).resolve().parent / 'registersingletontype.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.resize(200, 200)
        view.show()
        QTimer.singleShot(250, view.close)
        app.exec()
        self.assertEqual(finalResult, 499)


if __name__ == '__main__':
    unittest.main()
