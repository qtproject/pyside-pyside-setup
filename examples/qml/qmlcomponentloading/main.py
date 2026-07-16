# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""Load and drive a QML-defined type from Python via load_qml_component.

A ``Person`` type defined in ``person.qml`` is composed inside a plain
Python ``Employee`` class; its QML signal is connected to a Python slot
and its QML method is called from Python.
"""

import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQmlFeatures import load_qml_component


class Employee:
    """Plain Python class composing a QML Person object."""

    def __init__(self, person_factory, name, age, department):
        self.person = person_factory.create(name=name, age=age)
        self.department = department
        self.person.birthdayHappened.connect(self._on_birthday)

    def _on_birthday(self):
        print(f"{self.person.name} is now {self.person.age}!")

    def celebrate(self):
        self.person.celebrateBirthday()


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    main_qml = Path(__file__).resolve().parent / "Main.qml"
    engine.load(main_qml)
    if not engine.rootObjects():
        sys.exit(-1)

    person = load_qml_component(engine, "person.qml")  # create happens in Employee constructor
    emp = Employee(person, "Alice", 28, "Engineering")
    emp.celebrate()  # prints "Alice is now 29!"

    sys.exit(app.exec())
