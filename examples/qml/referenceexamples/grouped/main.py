# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the qml/examples/qml/referenceexamples/default example from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

from person import Boy, Girl
from birthdayparty import BirthdayParty


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    qml_file = Path(__file__).parent / "example.qml"
    url = QUrl.fromLocalFile(qml_file)
    engine = QQmlEngine()
    component = QQmlComponent(engine, url)
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
            best_shoe = guest;
    if best_shoe:
          print(f"{best_shoe.name} is wearing the best shoes!");
    del engine
    sys.exit(0)
