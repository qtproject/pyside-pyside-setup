# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QDate, QObject, ClassInfo, Property, QTime, Signal
from PySide6.QtQml import QmlAnonymous, QmlAttached, QmlElement, ListProperty

from person import Person


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "People"
QML_IMPORT_MAJOR_VERSION = 1


@QmlAnonymous
class BirthdayPartyAttached(QObject):

    rsvp_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rsvp = QDate()

    @Property(QDate, notify=rsvp_changed)
    def rsvp(self):
        return self._rsvp

    @rsvp.setter
    def rsvp(self, d):
        if self._rsvp != d:
            self._rsvp = d
            self.rsvp_changed.emit()


@QmlElement
@ClassInfo(DefaultProperty="guests")
@QmlAttached(BirthdayPartyAttached)
class BirthdayParty(QObject):

    partyStarted = Signal(QTime)
    host_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._host = None
        self._guests = []

    def startParty(self):
        self.partyStarted.emit(QTime.currentTime())

    @Property(Person, notify=host_changed)
    def host(self):
        return self._host

    @host.setter
    def host(self, h):
        if self._host != h:
            self._host = h
            self.host_changed.emit()

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
