# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the qml/examples/qml/referenceexamples/properties example from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

from person import Person  # noqa: F401
from birthdayparty import BirthdayParty  # noqa: F401


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    engine = QQmlEngine()
    engine.addImportPath(Path(__file__).parent)
    component = QQmlComponent(engine)
    component.loadFromModule("People", "Main")

    party = component.create()
    if party:
        print(f"{party.host} is having a birthday!\nThey are inviting:")
        for g in range(party.guestCount()):
            name = party.guest(g).name
            print(f"    {name}")
    else:
        print(component.errors())

    del engine
    sys.exit(0)
