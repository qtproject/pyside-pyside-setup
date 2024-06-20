# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the qml/examples/qml/referenceexamples/binding example from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine, qmlAttachedPropertiesObject

from person import Boy, Girl  # noqa: F401
from birthdayparty import BirthdayParty  # noqa: F401
from happybirthdaysong import HappyBirthdaySong  # noqa: F401


if __name__ == "__main__":
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
    for g in range(party.guestCount()):
        guest = party.guest(g)
        name = guest.name

        rsvp_date = None
        attached = qmlAttachedPropertiesObject(BirthdayParty, guest, False)
        if attached:
            rsvp_date = attached.rsvp.toString()
        if rsvp_date:
            print(f"    {name} RSVP date: {rsvp_date}")
        else:
            print(f"    {name} RSVP date: Hasn't RSVP'd")

    party.startParty()

    r = app.exec()

    del engine
    sys.exit(r)
