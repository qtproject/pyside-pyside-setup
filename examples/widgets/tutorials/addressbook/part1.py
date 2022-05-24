# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QGridLayout,
                               QLabel, QGridLayout, QLineEdit, QTextEdit,
                               QWidget)


class AddressBook(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        name_label = QLabel("Name:")
        self._name_line = QLineEdit()

        address_label = QLabel("Address:")
        self._address_text = QTextEdit()

        main_layout = QGridLayout()
        main_layout.addWidget(name_label, 0, 0)
        main_layout.addWidget(self._name_line, 0, 1)
        main_layout.addWidget(address_label, 1, 0, Qt.AlignTop)
        main_layout.addWidget(self._address_text, 1, 1)

        self.setLayout(main_layout)
        self.setWindowTitle("Simple Address Book")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    address_book = AddressBook()
    address_book.show()

    sys.exit(app.exec())
