# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtSerialPort import QSerialPort

from ui_settingsdialog import Ui_SettingsDialog


class Settings:
    def __init__(self):
        self.parity = QSerialPort.EvenParity
        self.baud = QSerialPort.Baud19200
        self.data_bits = QSerialPort.Data8
        self.stop_bits = QSerialPort.OneStop
        self.response_time = 1000
        self.number_of_retries = 3


class SettingsDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.m_settings = Settings()
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.ui.parityCombo.setCurrentIndex(1)
        self.ui.baudCombo.setCurrentText(f"{self.m_settings.baud}")
        self.ui.dataBitsCombo.setCurrentText(f"{self.m_settings.data_bits}")
        self.ui.stopBitsCombo.setCurrentText(f"{self.m_settings.stop_bits}")
        self.ui.timeoutSpinner.setValue(self.m_settings.response_time)
        self.ui.retriesSpinner.setValue(self.m_settings.number_of_retries)

        self.ui.applyButton.clicked.connect(self._apply)

    @Slot()
    def _apply(self):
        self.m_settings.parity = self.ui.parityCombo.currentIndex()
        if self.m_settings.parity > 0:
            self.m_settings.parity = self.m_settings.parity + 1
        self.m_settings.baud = int(self.ui.baudCombo.currentText())
        self.m_settings.data_bits = int(self.ui.dataBitsCombo.currentText())
        self.m_settings.stop_bits = int(self.ui.stopBitsCombo.currentText())
        self.m_settings.response_time = self.ui.timeoutSpinner.value()
        self.m_settings.number_of_retries = self.ui.retriesSpinner.value()

        self.hide()

    def settings(self):
        return self.m_settings
