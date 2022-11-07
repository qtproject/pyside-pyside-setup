# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import json
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
from PySide6.QtCore import QObject, Signal, Slot, QUrl
from PySide6.QtQml import QmlElement

"""PYSIDE-2098: Roundtrip test for signals using QVariantList/QVariantMap.

@QmlElement Obj has signals of list/dict type which are connected to an
instance of Connections in QML. The QML instance sends them back to Obj's
slots and additionally sends them back as stringified JSON. This verifies that
a conversion is done instead of falling back to the default PyObject
passthrough converter, resulting in a QVariant<PyObject> and reference leaks
on the PyObject.
"""

QML_IMPORT_NAME = "test.Obj"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Obj(QObject):
    listSignal = Signal(list)
    dictSignal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_data = None
        self._last_json_data = None

    def clear(self):
        self._last_data = None
        self._last_json_data = None

    def last_data(self):
        """Last data received."""
        return self._last_data

    def last_json_data(self):
        """Last data converted from JSON."""
        return self._last_json_data

    def emit_list(self, test_list):
        self.listSignal.emit(test_list)

    def emit_dict(self, test_dict):
        self.dictSignal.emit(test_dict)

    @Slot(list)
    def list_slot(self, l):
        self._last_data = l
        print("list_slot", l)

    @Slot(dict)
    def dict_slot(self, d):
        self._last_data = d
        print("dict_slot", d)

    @Slot(str)
    def json_slot(self, s):
        self._last_json_data = json.loads(s)
        print(f'json_slot "{s}"->', self._last_json_data)


class TestConnectionWithQml(TimedQGuiApplication):

    def setUp(self):
        super().setUp()
        self._view = QQuickView()
        self._obj = Obj()

        self._view.setInitialProperties({"o": self._obj})
        file = Path(__file__).resolve().parent / "signal_types.qml"
        self.assertTrue(file.is_file())
        self._view.setSource(QUrl.fromLocalFile(file))
        root = self._view.rootObject()
        self.assertTrue(root, quickview_errorstring(self._view))

    def tearDown(self):
        super().tearDown()
        del self._view
        self._view = None

    def testVariantList(self):
        self._obj.clear()
        test_list = [1, 2]
        before_refcount = sys.getrefcount(test_list)
        self._obj.emit_list(test_list)
        received = self._obj.last_data()
        self.assertTrue(isinstance(received, list))
        self.assertEqual(test_list, received)
        self.assertEqual(test_list, self._obj.last_json_data())
        refcount = sys.getrefcount(test_list)
        self.assertEqual(before_refcount, refcount)

    def testVariantDict(self):
        self._obj.clear()
        test_dict = {"1": 1, "2": 2}
        before_refcount = sys.getrefcount(test_dict)
        self._obj.emit_dict(test_dict)
        received = self._obj.last_data()
        self.assertTrue(isinstance(received, dict))
        self.assertEqual(test_dict, received)
        self.assertEqual(test_dict, self._obj.last_json_data())
        refcount = sys.getrefcount(test_dict)
        self.assertEqual(before_refcount, refcount)


if __name__ == "__main__":
    unittest.main()
