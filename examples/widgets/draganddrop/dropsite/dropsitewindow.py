# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import re
from PySide6.QtCore import QMimeData, Qt, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QAbstractItemView, QPushButton,
                               QDialogButtonBox, QLabel,
                               QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from droparea import DropArea

DESCRIPTION = """This example accepts drags from other applications and
displays the MIME types provided by the drag object."""


_WHITESPACE_PATTERN = re.compile(r"\s+")


def simplify_whitespace(s):
    return _WHITESPACE_PATTERN.sub(" ", s).strip()


class DropSiteWindow(QWidget):

    def __init__(self):
        super().__init__()
        drop_area = DropArea()
        abstract_label = QLabel()
        self._formats_table = QTableWidget()

        button_box = QDialogButtonBox()
        abstract_label = QLabel(DESCRIPTION)
        abstract_label.setWordWrap(True)
        abstract_label.adjustSize()

        drop_area = DropArea()
        drop_area.changed.connect(self.update_formats_table)

        self._formats_table = QTableWidget()
        self._formats_table.setColumnCount(2)
        self._formats_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._formats_table.setHorizontalHeaderLabels(["Format", "Content"])
        self._formats_table.horizontalHeader().setStretchLastSection(True)

        clear_button = QPushButton("Clear")
        self._copy_button = QPushButton("Copy")
        quit_button = QPushButton("Quit")

        button_box = QDialogButtonBox()
        button_box.addButton(clear_button, QDialogButtonBox.ActionRole)
        button_box.addButton(self._copy_button, QDialogButtonBox.ActionRole)
        self._copy_button.setVisible(False)

        button_box.addButton(quit_button, QDialogButtonBox.RejectRole)

        quit_button.clicked.connect(self.close)
        clear_button.clicked.connect(drop_area.clear)
        self._copy_button.clicked.connect(self.copy)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(abstract_label)
        main_layout.addWidget(drop_area)
        main_layout.addWidget(self._formats_table)
        main_layout.addWidget(button_box)

        self.setWindowTitle("Drop Site")
        self.resize(700, 500)

    @Slot(QMimeData)
    def update_formats_table(self, mime_data):
        self._formats_table.setRowCount(0)
        self._copy_button.setEnabled(False)
        if not mime_data:
            return

        for format in mime_data.formats():
            format_item = QTableWidgetItem(format)
            format_item.setFlags(Qt.ItemIsEnabled)
            format_item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)

            if format == "text/plain":
                text = simplify_whitespace(mime_data.text())
            elif format == "text/markdown":
                text = mime_data.data("text/markdown").data().decode("utf8")
            elif format == "text/html":
                text = simplify_whitespace(mime_data.html())
            elif format == "text/uri-list":
                url_list = mime_data.urls()
                text = ""
                for i in range(0, min(len(url_list), 32)):
                    text += url_list[i].toString() + " "
            else:
                data = mime_data.data(format)
                if data.size() > 32:
                    data.truncate(32)
                text = data.toHex(" ").data().decode("utf8").upper()

            row = self._formats_table.rowCount()
            self._formats_table.insertRow(row)
            self._formats_table.setItem(row, 0, QTableWidgetItem(format))
            self._formats_table.setItem(row, 1, QTableWidgetItem(text))

        self._formats_table.resizeColumnToContents(0)
        self._copy_button.setEnabled(self._formats_table.rowCount() > 0)

    @Slot()
    def copy(self):
        text = ""
        for row in range(0, self._formats_table.rowCount()):
            c1 = self._formats_table.item(row, 0).text()
            c2 = self._formats_table.item(row, 1).text()
            text += f"{c1}: {c2}\n"
        QGuiApplication.clipboard().setText(text)
