# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QDate, QObject, ClassInfo, Property, QTime, Signal
from PySide6.QtQml import QmlAnonymous, QmlAttached, QmlElement, ListProperty

from person import Person


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "examples.valuesource.people"
QML_IMPORT_MAJOR_VERSION = 1


@QmlAnonymous
class BirthdayPartyAttached(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rsvp = QDate()

    @Property(QDate)
    def rsvp(self):
        return self._rsvp

    @rsvp.setter
    def rsvp(self, d):
        self._rsvp = d


@QmlElement
@ClassInfo(DefaultProperty="guests")
@QmlAttached(BirthdayPartyAttached)
class BirthdayParty(QObject):

    partyStarted = Signal(QTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._host = None
        self._guests = []

    def startParty(self):
        self.partyStarted.emit(QTime.currentTime())

    @Property(Person)
    def host(self):
        return self._host

    @host.setter
    def host(self, h):
        self._host = h

    @Property(str)
    def announcement(self):
        return ""

    @announcement.setter
    def announcement(self, a):
        print(a)

    def guest(self, n):
        return self._guests[n]

    def guestCount(self):
        return len(self._guests)

    def appendGuest(self, guest):
        self._guests.append(guest)

    @staticmethod
    def qmlAttachedProperties(self, o):
        return BirthdayPartyAttached(o)

    guests = ListProperty(Person, appendGuest)
