# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QObject, ClassInfo, Property
from PySide6.QtQml import QmlElement, ListProperty

from person import Person


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "examples.grouped.people"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@ClassInfo(DefaultProperty="guests")
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
