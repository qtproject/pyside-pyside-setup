# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the qml/examples/qml/referenceexamples/adding example from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

from person import Person


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    qml_file = Path(__file__).parent / "example.qml"
    url = QUrl.fromLocalFile(qml_file)
    engine = QQmlEngine()
    component = QQmlComponent(engine, url)

    person = component.create()
    if person:
        print(f"The person's name is {person.name}")
        print(f"They wear a {person.shoe_size} sized shoe")
    else:
        print(component.errors())
    del engine
    sys.exit(0)
