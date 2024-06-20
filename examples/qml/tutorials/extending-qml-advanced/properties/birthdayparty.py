# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QObject, Property
from PySide6.QtQml import QmlElement, ListProperty

from person import Person


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "People"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class BirthdayParty(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._host = None
        self._guests = []

    @Property(Person)
    def host(self):
        return self._host

    @host.setter
    def host(self, h):
        self._host = h

    def guest(self, n):
        return self._guests[n]

    def guestCount(self):
        return len(self._guests)

    def appendGuest(self, guest):
        self._guests.append(guest)

    guests = ListProperty(Person, appendGuest)
