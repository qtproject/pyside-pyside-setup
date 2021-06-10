
#############################################################################
##
## Copyright (C) 2011 Arun Srinivasan  <rulfzid@gmail.com>
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
