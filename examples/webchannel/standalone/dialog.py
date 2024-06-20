# Copyright (C) 2017 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com, author Milian Wolff <milian.wolff@kdab.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations


from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog
from ui_dialog import Ui_Dialog


class Dialog(QDialog):
    send_text = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self._ui.send.clicked.connect(self.clicked)
        self._ui.input.returnPressed.connect(self._ui.send.animateClick)

    @Slot(str)
    def display_message(self, message):
        self._ui.output.appendPlainText(message)

    @Slot()
    def clicked(self):
        text = self._ui.input.text()
        if not text:
            return
        self.send_text.emit(text)
        self.display_message(f"Sent message: {text}")
        self._ui.input.clear()
