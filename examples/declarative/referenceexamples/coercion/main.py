# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the qml/examples/qml/referenceexamples/coercion example from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

from person import Boy, Girl
from birthdayparty import BirthdayParty


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
for g in range(party.guestCount()):
    name = party.guest(g).name
    print(f"    {name}")
del engine
sys.exit(0)
