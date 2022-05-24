# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from typing import List

from PySide6.QtCore import QMimeDatabase, QMimeType, QModelIndex, QObject, Qt, qWarning
from PySide6.QtGui import QStandardItem, QStandardItemModel

mimeTypeRole = Qt.UserRole + 1
iconQueriedRole = Qt.UserRole + 2


def createRow(t: QMimeType):
    name_item = QStandardItem(t.name())
    flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
    name_item.setData(t, mimeTypeRole)
    name_item.setData(False, iconQueriedRole)
    name_item.setFlags(flags)
    name_item.setToolTip(t.comment())
    return [name_item]


class MimeTypeModel(QStandardItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(0, 1, parent)
        self.setHorizontalHeaderLabels(["Name"])
        self.m_name_index_hash = {}
        self.populate()

    def populate(self):
        mime_database = QMimeDatabase()
        all_types: List[QMimeType] = mime_database.allMimeTypes()

        # Move top level types to rear end of list, sort this partition,
        # create top level items and truncate the list.
        with_parent_mimetypes, without_parent_mimetypes = [], []

        for mime_type in all_types:
            if mime_type.parentMimeTypes():
                with_parent_mimetypes.append(mime_type)
            else:
                without_parent_mimetypes.append(mime_type)

        without_parent_mimetypes.sort(key=lambda x: x.name())

        for top_level_type in without_parent_mimetypes:
            row = createRow(top_level_type)
            self.appendRow(row)
            self.m_name_index_hash[top_level_type.name()] = self.indexFromItem(row[0])

        all_types = with_parent_mimetypes

        while all_types:
            # Find a type inheriting one that is already in the model.
            name_index_value: QModelIndex = None
            name_index_key = ""
            for mime_type in all_types:
                name_index_value = self.m_name_index_hash.get(
                    mime_type.parentMimeTypes()[0]
                )
                if name_index_value:
                    name_index_key = mime_type.parentMimeTypes()[0]
                    break

            if not name_index_value:
                orphaned_mime_types = ", ".join(
                    [mime_type.name() for mime_type in all_types]
                )
                qWarning(f"Orphaned mime types: {orphaned_mime_types}")
                break

            # Move types inheriting the parent type to rear end of list, sort this partition,
            # append the items to parent and truncate the list.
            parent_name = name_index_key
            with_parent_name, without_parent_name = [], []

            for mime_type in all_types:
                if parent_name in mime_type.parentMimeTypes():
                    with_parent_name.append(mime_type)
                else:
                    without_parent_name.append(mime_type)

            without_parent_name.sort(key=lambda x: x.name())
            parent_item = self.itemFromIndex(name_index_value)

            for mime_type in with_parent_name:
                row = createRow(mime_type)
                parent_item.appendRow(row)
                self.m_name_index_hash[mime_type.name()] = self.indexFromItem(row[0])

            all_types = without_parent_name

    def mimeType(self, index: QModelIndex):
        return index.data(mimeTypeRole)

    def indexForMimeType(self, name):
        return self.m_name_index_hash[name]

    @staticmethod
    def formatMimeTypeInfo(t: QMimeType):
        out = f"<html><head/><body><h3><center>{t.name()}</center></h3><br><table>"
        aliases_str = ", ".join(t.aliases())
        if aliases_str:
            out += f"<tr><td>Aliases:</td><td> ({aliases_str})"

        out += (
            f"</td></tr><tr><td>Comment:</td><td>{t.comment()}"
            f"</td></tr><tr><td>Icon name:</td><td>{t.iconName()}</td></tr>"
            f"<tr><td>Generic icon name</td><td>{t.genericIconName()}</td></tr>"
        )

        filter_str = t.filterString()
        if filter_str:
            out += f"<tr><td>Filter:</td><td>{filter_str}</td></tr>"

        patterns_str = ", ".join(t.globPatterns())
        if patterns_str:
            out += f"<tr><td>Glob patterns:</td><td>{patterns_str}</td></tr>"

        parentMimeTypes_str = ", ".join(t.parentMimeTypes())
        if parentMimeTypes_str:
            out += f"<tr><td>Parent types:</td><td>{parentMimeTypes_str}</td></tr>"

        suffixes = t.suffixes()
        if suffixes:
            out += "<tr><td>Suffixes:</td><td>"
            preferredSuffix = t.preferredSuffix()
            if preferredSuffix:
                suffixes.remove(preferredSuffix)
                out += f"<b>{preferredSuffix}</b> "
            suffixes_str = ", ".join(suffixes)
            out += f"{suffixes_str}</td></tr>"

        out += "</table></body></html>"

        return out
