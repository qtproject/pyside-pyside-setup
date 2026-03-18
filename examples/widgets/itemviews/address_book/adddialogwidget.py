# Copyright (C) 2011 Arun Srinivasan <rulfzid@gmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QDialog, QFormLayout, QPlainTextEdit, QLineEdit,
                               QDialogButtonBox, QVBoxLayout)


class AddDialogWidget(QDialog):
    """ A dialog to add a new address to the addressbook. """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                            | QDialogButtonBox.StandardButton.Cancel)

        self._name_text = QLineEdit()
        self._address_text = QPlainTextEdit()

        formLayout = QFormLayout()
        formLayout.addRow("Name", self._name_text)
        formLayout.addRow("Address", self._address_text)

        layout = QVBoxLayout(self)
        layout.addLayout(formLayout)
        layout.addWidget(self._button_box)

        self.setWindowTitle("Add a Contact")

        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        self._name_text.textChanged.connect(self._updateEnabled)
        self._address_text.textChanged.connect(self._updateEnabled)

        self._updateEnabled()

    @Slot()
    def _updateEnabled(self):
        name = self.name
        address = self.address
        enabled = bool(name) and name[:1].isalpha() and bool(address)
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

    # These properties make using this dialog a little cleaner. It's much
    # nicer to type "addDialog.address" to retrieve the address as compared
    # to "addDialog.addressText.toPlainText()"
    @property
    def name(self):
        return self._name_text.text()

    @name.setter
    def name(self, n):
        self._name_text.setText(n)

    @property
    def name_enabled(self):
        return self._name_text.isEnabled()

    @name_enabled.setter
    def name_enabled(self, e):
        self._name_text.setEnabled(e)

    @property
    def address(self):
        return self._address_text.toPlainText()

    @address.setter
    def address(self, a):
        self._address_text.setPlainText(a)
