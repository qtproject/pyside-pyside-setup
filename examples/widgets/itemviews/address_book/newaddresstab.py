# Copyright (C) 2011 Arun Srinivasan  <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout


class NewAddressTab(QWidget):
    """ An extra tab that prompts the user to add new contacts.
        To be displayed only when there are no contacts in the model.
    """

    triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        description_label = QLabel("There are no contacts in your address book."
                                   "\nClick Add to add new contacts.")

        add_button = QPushButton("Add")

        layout = QVBoxLayout(self)
        layout.addWidget(description_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(add_button, 0, Qt.AlignmentFlag.AlignCenter)

        add_button.clicked.connect(self.triggered)
