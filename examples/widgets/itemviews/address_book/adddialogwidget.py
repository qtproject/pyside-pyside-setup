# Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QLabel, QTextEdit, QLineEdit,
                               QDialogButtonBox, QGridLayout, QVBoxLayout)


class AddDialogWidget(QDialog):
    """ A dialog to add a new address to the addressbook. """

    def __init__(self, parent=None):
        super().__init__(parent)

        name_label = QLabel("Name")
        address_label = QLabel("Address")
        button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                      QDialogButtonBox.Cancel)

        self._name_text = QLineEdit()
        self._address_text = QTextEdit()

        grid = QGridLayout()
        grid.setColumnStretch(1, 2)
        grid.addWidget(name_label, 0, 0)
        grid.addWidget(self._name_text, 0, 1)
        grid.addWidget(address_label, 1, 0, Qt.AlignLeft | Qt.AlignTop)
        grid.addWidget(self._address_text, 1, 1, Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.setWindowTitle("Add a Contact")

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    # These properties make using this dialog a little cleaner. It's much
    # nicer to type "addDialog.address" to retrieve the address as compared
    # to "addDialog.addressText.toPlainText()"
    @property
    def name(self):
        return self._name_text.text()

    @property
    def address(self):
        return self._address_text.toPlainText()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dialog = AddDialogWidget()
    if (dialog.exec()):
        name = dialog.name
        address = dialog.address
        print(f"Name: {name}")
        print(f"Address: {address}")
