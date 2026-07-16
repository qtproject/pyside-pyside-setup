# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlEngine
from PySide6.QtQmlFeatures import load_qml_component

PERSON_QML = """\
import QtQuick

QtObject {
    property string name: "John"
    property int age: 30
    property var items: []
    property var metadata: ({})
    signal birthdayHappened()
    function celebrateBirthday() {
        age++
        birthdayHappened()
    }
}
"""


def _write(tmp: Path, text: str, name: str = "person.qml") -> Path:
    p = tmp / name
    p.write_text(text)
    return p


class QmlComponentTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication(sys.argv)

    def setUp(self):
        self.engine = QQmlEngine()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        del self.engine
        self._tmp.cleanup()

    def test_factory_from_file(self):
        qml = _write(self.tmp, PERSON_QML)
        factory = load_qml_component(self.engine, str(qml))
        self.assertIn("person.qml", repr(factory))

    def test_factory_from_module(self):
        factory = load_qml_component(self.engine, module="QtQuick",
                                     type_name="QtObject")
        self.assertIn("QtQuick", repr(factory))

    def test_requires_source_or_module(self):
        with self.assertRaises(ValueError):
            load_qml_component(self.engine)

    def test_requires_engine(self):
        with self.assertRaises(TypeError):
            load_qml_component(None, "person.qml")

    def test_read_default_properties(self):
        person = load_qml_component(self.engine,
                                    str(_write(self.tmp, PERSON_QML))).create()
        self.assertEqual(person.name, "John")
        self.assertEqual(person.age, 30)

    def test_write_properties(self):
        person = load_qml_component(self.engine,
                                    str(_write(self.tmp, PERSON_QML))).create()
        person.name = "Alice"
        person.age = 25
        self.assertEqual(person.name, "Alice")
        self.assertEqual(person.age, 25)

    def test_create_with_initial_properties(self):
        person = load_qml_component(
            self.engine, str(_write(self.tmp, PERSON_QML))
        ).create(name="Bob", age=42)
        self.assertEqual(person.name, "Bob")
        self.assertEqual(person.age, 42)

    def test_qobject_escape_hatch(self):
        person = load_qml_component(self.engine,
                                    str(_write(self.tmp, PERSON_QML))).create()
        self.assertEqual(person.qobject.property("name"), "John")

    def test_signal_connect_and_method_call(self):
        person = load_qml_component(self.engine,
                                    str(_write(self.tmp, PERSON_QML))).create()
        fired = []
        person.birthdayHappened.connect(lambda: fired.append(1))
        person.celebrateBirthday()
        self.assertEqual(len(fired), 1)
        self.assertEqual(person.age, 31)

    def test_assign_list_and_dict(self):
        obj = load_qml_component(self.engine,
                                 str(_write(self.tmp, PERSON_QML))).create()
        obj.items = [1, "two", 3.0]
        self.assertEqual(list(obj.items), [1, "two", 3.0])
        obj.metadata = {"key": "value", "count": 42}
        self.assertEqual(obj.metadata["count"], 42)

    def test_missing_file_raises(self):
        factory = load_qml_component(self.engine, str(self.tmp / "nope.qml"))
        with self.assertRaises(RuntimeError):
            factory.create()

    def test_malformed_qml_raises(self):
        bad = _write(self.tmp, "not valid QML {{{", name="bad.qml")
        with self.assertRaises(RuntimeError):
            load_qml_component(self.engine, str(bad)).create()

    def test_unknown_attribute_raises(self):
        obj = load_qml_component(self.engine,
                                 str(_write(self.tmp, PERSON_QML))).create()
        with self.assertRaises(AttributeError):
            _ = obj.no_such_thing

    def test_python_only_attribute(self):
        obj = load_qml_component(self.engine,
                                 str(_write(self.tmp, PERSON_QML))).create()
        obj._custom = 42
        self.assertEqual(obj._custom, 42)

    def test_repr(self):
        obj = load_qml_component(self.engine,
                                 str(_write(self.tmp, PERSON_QML))).create()
        self.assertIn("QmlObject", repr(obj))


if __name__ == "__main__":
    unittest.main()
