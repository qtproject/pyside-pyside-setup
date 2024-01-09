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

from PySide6.QtCore import Property, Signal, QTimer, QUrl, QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import (qmlRegisterSingletonType, qmlRegisterSingletonInstance,
                           QmlElement, QmlSingleton, QJSValue)
from PySide6.QtQuick import QQuickView


URI = "Singletons"


finalResult = 0
qObjectQmlTypeId = 0


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


QML_IMPORT_NAME = URI
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


@QmlElement
@QmlSingleton
class DecoratedSingletonWithCreate(QObject):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data

    @staticmethod
    def create(engine):
        return DecoratedSingletonWithCreate(400)

    def getData(self):
        return self._data

    def setData(self, data):
        self._data = data

    data = Property(int, getData, setData)


class TestQuickView(QQuickView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._singleton_instance_qobject_int = False
        self._singleton_instance_qobject_str = False
        self._singleton_instance_jsvalue_int = False

    @Slot()
    def testSlot(self):
        engine = self.engine()
        instance = engine.singletonInstance(qObjectQmlTypeId)
        if instance is not None and isinstance(instance, QObject):
            self._singleton_instance_qobject_int = True
        instance = engine.singletonInstance(URI, 'SingletonQObjectNoCallback')
        if instance is not None and isinstance(instance, QObject):
            self._singleton_instance_qobject_str = True
        instance = engine.singletonInstance(URI, 'SingletonQJSValue')
        if instance is not None and isinstance(instance, QJSValue):
            self._singleton_instance_jsvalue_int = True
        self.close()


class TestQmlSupport(unittest.TestCase):
    def testIt(self):
        app = QGuiApplication([])

        qObjectQmlTypeId = qmlRegisterSingletonType(SingletonQObject, URI, 1, 0,
                                                    'SingletonQObjectNoCallback')
        qmlRegisterSingletonType(SingletonQObject, URI, 1, 0, 'SingletonQObjectCallback',
                                 singletonQObjectCallback)

        qmlRegisterSingletonType(URI, 1, 0, 'SingletonQJSValue', singletonQJSValueCallback)

        # Accepts only QObject derived types
        l = [1, 2]
        with self.assertRaises(TypeError):
            qmlRegisterSingletonInstance(SingletonQObject, URI, 1, 0, 'SingletonInstance', l)

        # Modify value on the instance
        s = SingletonQObject()
        s.setData(99)
        qmlRegisterSingletonInstance(SingletonQObject, URI, 1, 0, 'SingletonInstance', s)

        view = TestQuickView()
        file = Path(__file__).resolve().parent / 'registersingletontype.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.resize(200, 200)
        view.show()
        QTimer.singleShot(250, view.testSlot)
        app.exec()
        self.assertEqual(finalResult, 899)
        self.assertTrue(view._singleton_instance_qobject_int)
        self.assertTrue(view._singleton_instance_qobject_str)
        self.assertTrue(view._singleton_instance_jsvalue_int)


if __name__ == '__main__':    unittest.main()
