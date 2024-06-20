# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the qml/examples/qml/referenceexamples/adding example from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

from person import Person  # noqa: F401


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    engine = QQmlEngine()
    engine.addImportPath(Path(__file__).parent)
    component = QQmlComponent(engine)
    component.loadFromModule("People", "Main")

    person = component.create()
    if person:
        print(f"The person's name is {person.name}")
        print(f"They wear a {person.shoe_size} sized shoe")
    else:
        print(component.errors())
    del engine
    sys.exit(0)
