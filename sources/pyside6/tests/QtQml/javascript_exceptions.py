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

from PySide6.QtCore import Slot, Property, Signal, QObject, QUrl
from PySide6.QtQml import QJSEngine, qmlRegisterType
from PySide6.QtQuick import QQuickView

test_error_message = "This is an error."

method_test_string = """
(function (obj) {
    obj.methodThrows();
})
"""

property_test_string = """
(function (obj) {
    obj.propertyThrows;
})
"""

test_1 = False
test_2 = False


class TestClass(QObject):
    @Slot()
    def methodThrows(self):
        raise TypeError(test_error_message)

    @Property(str)
    def propertyThrows(self):
        raise TypeError(test_error_message)

    @Slot(int)
    def passTest(self, test):
        global test_1, test_2

        if test == 1:
            test_1 = True
        else:
            test_2 = True


class JavaScriptExceptionsTest(UsesQApplication):
    def test_jsengine(self):
        engine = QJSEngine()
        test_object = TestClass()
        test_value = engine.newQObject(test_object)

        result_1 = engine.evaluate(method_test_string).call([test_value])

        self.assertTrue(result_1.isError())
        self.assertEqual(result_1.property('message').toString(), test_error_message)
        self.assertEqual(result_1.property('name').toString(), 'TypeError')

        result_2 = engine.evaluate(property_test_string).call([test_value])

        self.assertTrue(result_2.isError())
        self.assertEqual(result_2.property('message').toString(), test_error_message)
        self.assertEqual(result_2.property('name').toString(), 'TypeError')

    def test_qml_type(self):
        qmlRegisterType(TestClass, 'JavaScriptExceptions', 1, 0, 'JavaScriptExceptions')

        view = QQuickView()
        file = Path(__file__).resolve().parent / 'javascript_exceptions.qml'
        self.assertTrue(file.is_file())
        qml_url = QUrl.fromLocalFile(file)

        view.setSource(qml_url)
        self.assertTrue(view.rootObject(), quickview_errorstring(view))

        self.assertTrue(test_1)
        self.assertTrue(test_2)


if __name__ == '__main__':
    unittest.main()
