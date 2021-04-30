
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2016 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

import sys

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QTextEdit,
                               QVBoxLayout, QWidget)


class SortedDict(dict):
    class Iterator(object):
        def __init__(self, sorted_dict):
            self._dict = sorted_dict
            self._keys = sorted(self._dict.keys())
            self._nr_items = len(self._keys)
            self._idx = 0

        def __iter__(self):
            return self

        def next(self):
            if self._idx >= self._nr_items:
                raise StopIteration

            key = self._keys[self._idx]
            value = self._dict[key]
            self._idx += 1

            return key, value

        __next__ = next

    def __iter__(self):
        return SortedDict.Iterator(self)

    iterkeys = __iter__


class AddressBook(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.contacts = SortedDict()
        self._old_name = ''
        self._old_address = ''

        name_label = QLabel("Name:")
        self._name_line = QLineEdit()
        self._name_line.setReadOnly(True)

        address_label = QLabel("Address:")
        self._address_text = QTextEdit()
        self._address_text.setReadOnly(True)

        self._add_button = QPushButton("&Add")
        self._submit_button = QPushButton("&Submit")
        self._submit_button.hide()
        self._cancel_button = QPushButton("&Cancel")
        self._cancel_button.hide()
        self._next_button = QPushButton("&Next")
        self._next_button.setEnabled(False)
        self._previous_button = QPushButton("&Previous")
        self._previous_button.setEnabled(False)

        self._add_button.clicked.connect(self.add_contact)
        self._submit_button.clicked.connect(self.submit_contact)
        self._cancel_button.clicked.connect(self.cancel)
        self._next_button.clicked.connect(self.next)
        self._previous_button.clicked.connect(self.previous)

        button_layout_1 = QVBoxLayout()
        button_layout_1.addWidget(self._add_button, Qt.AlignTop)
        button_layout_1.addWidget(self._submit_button)
        button_layout_1.addWidget(self._cancel_button)
        button_layout_1.addStretch()

        button_layout_2 = QHBoxLayout()
        button_layout_2.addWidget(self._previous_button)
        button_layout_2.addWidget(self._next_button)

        main_layout = QGridLayout()
        main_layout.addWidget(name_label, 0, 0)
        main_layout.addWidget(self._name_line, 0, 1)
        main_layout.addWidget(address_label, 1, 0, Qt.AlignTop)
        main_layout.addWidget(self._address_text, 1, 1)
        main_layout.addLayout(button_layout_1, 1, 2)
        main_layout.addLayout(button_layout_2, 3, 1)

        self.setLayout(main_layout)
        self.setWindowTitle("Simple Address Book")

    def add_contact(self):
        self._old_name = self._name_line.text()
        self._old_address = self._address_text.toPlainText()

        self._name_line.clear()
        self._address_text.clear()

        self._name_line.setReadOnly(False)
        self._name_line.setFocus(Qt.OtherFocusReason)
        self._address_text.setReadOnly(False)

        self._add_button.setEnabled(False)
        self._next_button.setEnabled(False)
        self._previous_button.setEnabled(False)
        self._submit_button.show()
        self._cancel_button.show()

    def submit_contact(self):
        name = self._name_line.text()
        address = self._address_text.toPlainText()

        if name == "" or address == "":
            QMessageBox.information(self, "Empty Field",
                    "Please enter a name and address.")
            return

        if name not in self.contacts:
            self.contacts[name] = address
            QMessageBox.information(self, "Add Successful",
                    f'"{name}" has been added to your address book.')
        else:
            QMessageBox.information(self, "Add Unsuccessful",
                    f'Sorry, "{name}" is already in your address book.')
            return

        if not self.contacts:
            self._name_line.clear()
            self._address_text.clear()

        self._name_line.setReadOnly(True)
        self._address_text.setReadOnly(True)
        self._add_button.setEnabled(True)

        number = len(self.contacts)
        self._next_button.setEnabled(number > 1)
        self._previous_button.setEnabled(number > 1)

        self._submit_button.hide()
        self._cancel_button.hide()

    def cancel(self):
        self._name_line.setText(self._old_name)
        self._address_text.setText(self._old_address)

        if not self.contacts:
            self._name_line.clear()
            self._address_text.clear()

        self._name_line.setReadOnly(True)
        self._address_text.setReadOnly(True)
        self._add_button.setEnabled(True)

        number = len(self.contacts)
        self._next_button.setEnabled(number > 1)
        self._previous_button.setEnabled(number > 1)

        self._submit_button.hide()
        self._cancel_button.hide()

    def next(self):
        name = self._name_line.text()
        it = iter(self.contacts)

        try:
            while True:
                this_name, _ = it.next()

                if this_name == name:
                    next_name, next_address = it.next()
                    break
        except StopIteration:
            next_name, next_address = iter(self.contacts).next()

        self._name_line.setText(next_name)
        self._address_text.setText(next_address)

    def previous(self):
        name = self._name_line.text()

        prev_name = prev_address = None
        for this_name, this_address in self.contacts:
            if this_name == name:
                break

            prev_name = this_name
            prev_address = this_address
        else:
            self._name_line.clear()
            self._address_text.clear()
            return

        if prev_name is None:
            for prev_name, prev_address in self.contacts:
                pass

        self._name_line.setText(prev_name)
        self._address_text.setText(prev_address)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    address_book = AddressBook()
    address_book.show()

    sys.exit(app.exec())
