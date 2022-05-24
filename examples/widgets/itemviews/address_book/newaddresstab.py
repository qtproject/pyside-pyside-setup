# Copyright (C) 2011 Arun Srinivasan  <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import (Qt, Signal)
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout)

from adddialogwidget import AddDialogWidget


class NewAddressTab(QWidget):
    """ An extra tab that prompts the user to add new contacts.
        To be displayed only when there are no contacts in the model.
    """

    send_details = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        description_label = QLabel("There are no contacts in your address book."
                                   "\nClick Add to add new contacts.")

        add_button = QPushButton("Add")

        layout = QVBoxLayout()
        layout.addWidget(description_label)
        layout.addWidget(add_button, 0, Qt.AlignCenter)

        self.setLayout(layout)

        add_button.clicked.connect(self.add_entry)

    def add_entry(self):
        add_dialog = AddDialogWidget()

        if add_dialog.exec():
            name = add_dialog.name
            address = add_dialog.address
            self.send_details.emit(name, address)


if __name__ == "__main__":

    def print_address(name, address):
        print(f"Name: {name}")
        print(f"Address: {address}")

    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    new_address_tab = NewAddressTab()
    new_address_tab.send_details.connect(print_address)
    new_address_tab.show()
    sys.exit(app.exec())
