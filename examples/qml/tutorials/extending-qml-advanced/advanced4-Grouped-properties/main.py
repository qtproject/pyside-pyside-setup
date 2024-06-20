# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the
   qml/examples/qml/tutorials/extending-qml-advanced/advanced4-Grouped-properties example
   from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

from person import Boy, Girl  # noqa: F401
from birthdayparty import BirthdayParty  # noqa: F401


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    engine = QQmlEngine()
    engine.addImportPath(Path(__file__).parent)
    component = QQmlComponent(engine)
    component.loadFromModule("People", "Main")

    party = component.create()
    if not party:
        print(component.errors())
        del engine
        sys.exit(-1)
    host = party.host
    print(f"{host.name} is having a birthday!")
    if isinstance(host, Boy):
        print("He is inviting:")
    else:
        print("She is inviting:")
    best_shoe = None
    for g in range(party.guestCount()):
        guest = party.guest(g)
        name = guest.name
        print(f"    {name}")
        if not best_shoe or best_shoe.shoe.price < guest.shoe.price:
            best_shoe = guest
    if best_shoe:
        print(f"{best_shoe.name} is wearing the best shoes!")
    del engine
    sys.exit(0)
