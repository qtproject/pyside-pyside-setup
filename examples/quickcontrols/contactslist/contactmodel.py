# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import bisect
from dataclasses import dataclass
from enum import IntEnum

from PySide6.QtCore import (QAbstractListModel, QEnum, Qt, QModelIndex, Slot,
                            QByteArray)
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "Backend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class ContactModel(QAbstractListModel):

    @QEnum
    class ContactRole(IntEnum):
        FullNameRole = Qt.ItemDataRole.DisplayRole
        AddressRole = Qt.ItemDataRole.UserRole
        CityRole = Qt.ItemDataRole.UserRole + 1
        NumberRole = Qt.ItemDataRole.UserRole + 2

    @dataclass
    class Contact:
        fullName: str
        address: str
        city: str
        number: str

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.m_contacts = []
        self.m_contacts.append(self.Contact("Angel Hogan", "Chapel St. 368 ", "Clearwater",
                                            "0311 1823993"))
        self.m_contacts.append(self.Contact("Felicia Patton", "Annadale Lane 2", "Knoxville",
                                            "0368 1244494"))
        self.m_contacts.append(self.Contact("Grant Crawford", "Windsor Drive 34", "Riverdale",
                                            "0351 7826892"))
        self.m_contacts.append(self.Contact("Gretchen Little", "Sunset Drive 348", "Virginia Beach",
                                            "0343 1234991"))
        self.m_contacts.append(self.Contact("Geoffrey Richards", "University Lane 54", "Trussville",
                                            "0423 2144944"))
        self.m_contacts.append(self.Contact("Henrietta Chavez", "Via Volto San Luca 3",
                                            "Piobesi Torinese", "0399 2826994"))
        self.m_contacts.append(self.Contact("Harvey Chandler", "North Squaw Creek 11",
                                            "Madisonville", "0343 1244492"))
        self.m_contacts.append(self.Contact("Miguel Gomez", "Wild Rose Street 13", "Trussville",
                                            "0343 9826996"))
        self.m_contacts.append(self.Contact("Norma Rodriguez", " Glen Eagles Street  53",
                                            "Buffalo", "0241 5826596"))
        self.m_contacts.append(self.Contact("Shelia Ramirez", "East Miller Ave 68", "Pickerington",
                                            "0346 4844556"))
        self.m_contacts.append(self.Contact("Stephanie Moss", "Piazza Trieste e Trento 77",
                                            "Roata Chiusani", "0363 0510490"))

    def rowCount(self, parent=QModelIndex()):
        return len(self.m_contacts)

    def data(self, index: QModelIndex, role: int):
        row = index.row()
        if row < self.rowCount():
            if role == ContactModel.ContactRole.FullNameRole:
                return self.m_contacts[row].fullName
            elif role == ContactModel.ContactRole.AddressRole:
                return self.m_contacts[row].address
            elif role == ContactModel.ContactRole.CityRole:
                return self.m_contacts[row].city
            elif role == ContactModel.ContactRole.NumberRole:
                return self.m_contacts[row].number

    def roleNames(self):
        default = super().roleNames()
        default[ContactModel.ContactRole.FullNameRole] = QByteArray(b"fullName")
        default[ContactModel.ContactRole.AddressRole] = QByteArray(b"address")
        default[ContactModel.ContactRole.CityRole] = QByteArray(b"city")
        default[ContactModel.ContactRole.NumberRole] = QByteArray(b"number")
        return default

    @Slot(int)
    def get(self, row: int):
        contact = self.m_contacts[row]
        return {"fullName": contact.fullName, "address": contact.address,
                "city": contact.city, "number": contact.number}

    @Slot(str, str, str, str)
    def append(self, full_name: str, address: str, city: str, number: str):
        contact = self.Contact(full_name, address, city, number)
        contact_names = [contact.fullName for contact in self.m_contacts]
        index = bisect.bisect(contact_names, contact.fullName)
        self.beginInsertRows(QModelIndex(), index, index)
        self.m_contacts.insert(index, contact)
        self.endInsertRows()

    @Slot(int, str, str, str, str)
    def set(self, row: int, full_name: str, address: str, city: str, number: str):
        if row < 0 or row >= len(self.m_contacts):
            return

        self.m_contacts[row] = self.Contact(full_name, address, city, number)
        self.dataChanged(self.index(row, 0), self.index(row, 0),
                         [ContactModel.ContactRole.FullNameRole,
                          ContactModel.ContactRole.AddressRole,
                          ContactModel.ContactRole.CityRole,
                          ContactModel.ContactRole.NumberRole])

    @Slot(int)
    def remove(self, row):
        if row < 0 or row >= len(self.m_contacts):
            return

        self.beginRemoveRows(QModelIndex(), row, row)
        del self.m_contacts[row]
        self.endRemoveRows()
