# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QComboBox
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo

from PySide6.QtWidgets import QDialog

from ui_settingsdialog import Ui_SettingsDialog


BLANK_STRING = "N/A"


CUSTOM_BAUDRATE_INDEX = 4


class Settings():

    def __init__(self):
        self.name = ""
        self.baud_rate = 0
        self.string_baud_rate = ""
        self.data_bits = QSerialPort.Data8
        self.string_data_bits = ""
        self.parity = QSerialPort.NoParity
        self.string_parity = ""
        self.stop_bits =  QSerialPort.OneStop
        self.string_stop_bits = ""
        self.flow_control = QSerialPort.SoftwareControl
        self.string_flow_control = ""
        self.local_echo_enabled = False


class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_ui = Ui_SettingsDialog()
        self._custom_port_index = -1
        self.m_ui.setupUi(self)
        self.m_currentSettings = Settings()
        self.m_intValidator = QIntValidator(0, 4000000, self)

        self.m_ui.baudRateBox.setInsertPolicy(QComboBox.NoInsert)

        self.m_ui.applyButton.clicked.connect(self.apply)
        self.m_ui.serialPortInfoListBox.currentIndexChanged.connect(self.show_port_info)
        self.m_ui.baudRateBox.currentIndexChanged.connect(self.check_custom_baud_rate_policy)
        self.m_ui.serialPortInfoListBox.currentIndexChanged.connect(self.check_custom_device_path_policy)

        self.fill_ports_parameters()
        self.fill_ports_info()

        self.update_settings()

    def settings(self):
        return self.m_currentSettings

    @Slot(int)
    def show_port_info(self, idx):
        if idx == -1:
            return

        list = self.m_ui.serialPortInfoListBox.itemData(idx)
        count = len(list) if list else 0
        description = list[1] if count > 1 else BLANK_STRING
        self.m_ui.descriptionLabel.setText(f"Description: {description}")
        manufacturer = list[2] if count > 2 else BLANK_STRING
        self.m_ui.manufacturerLabel.setText(f"Manufacturer: {manufacturer}")
        serialno = list[3] if count > 3 else BLANK_STRING
        self.m_ui.serialNumberLabel.setText(f"Serial number: {serialno}")
        location = list[4] if count > 4 else BLANK_STRING
        self.m_ui.locationLabel.setText(f"Location: {location}")
        vendor = list[5] if count > 5 else BLANK_STRING
        self.m_ui.vidLabel.setText(f"Vendor Identifier: {vendor}")
        id = list[6] if count > 6 else BLANK_STRING
        self.m_ui.pidLabel.setText(f"Product Identifier: {id}")

    @Slot()
    def apply(self):
        self.update_settings()
        self.hide()

    @Slot(int)
    def check_custom_baud_rate_policy(self, idx):
        is_custom_baud_rate = idx == CUSTOM_BAUDRATE_INDEX
        self.m_ui.baudRateBox.setEditable(is_custom_baud_rate)
        if is_custom_baud_rate:
            self.m_ui.baudRateBox.clearEditText()
            edit = self.m_ui.baudRateBox.lineEdit()
            edit.setValidator(self.m_intValidator)

    @Slot(int)
    def check_custom_device_path_policy(self, idx):
        is_custom_path = idx == self._custom_port_index
        self.m_ui.serialPortInfoListBox.setEditable(is_custom_path)
        if is_custom_path:
            self.m_ui.serialPortInfoListBox.clearEditText()

    def fill_ports_parameters(self):
        self.m_ui.baudRateBox.addItem("9600", QSerialPort.Baud9600)
        self.m_ui.baudRateBox.addItem("19200", QSerialPort.Baud19200)
        self.m_ui.baudRateBox.addItem("38400", QSerialPort.Baud38400)
        self.m_ui.baudRateBox.addItem("115200", QSerialPort.Baud115200)
        self.m_ui.baudRateBox.addItem("Custom")

        self.m_ui.dataBitsBox.addItem("5", QSerialPort.Data5)
        self.m_ui.dataBitsBox.addItem("6", QSerialPort.Data6)
        self.m_ui.dataBitsBox.addItem("7", QSerialPort.Data7)
        self.m_ui.dataBitsBox.addItem("8", QSerialPort.Data8)
        self.m_ui.dataBitsBox.setCurrentIndex(3)

        self.m_ui.parityBox.addItem("None", QSerialPort.NoParity)
        self.m_ui.parityBox.addItem("Even", QSerialPort.EvenParity)
        self.m_ui.parityBox.addItem("Odd", QSerialPort.OddParity)
        self.m_ui.parityBox.addItem("Mark", QSerialPort.MarkParity)
        self.m_ui.parityBox.addItem("Space", QSerialPort.SpaceParity)

        self.m_ui.stopBitsBox.addItem("1", QSerialPort.OneStop)
        if sys.platform == "win32":
            self.m_ui.stopBitsBox.addItem("1.5", QSerialPort.OneAndHalfStop)

        self.m_ui.stopBitsBox.addItem("2", QSerialPort.TwoStop)

        self.m_ui.flowControlBox.addItem("None", QSerialPort.NoFlowControl)
        self.m_ui.flowControlBox.addItem("RTS/CTS", QSerialPort.HardwareControl)
        self.m_ui.flowControlBox.addItem("XON/XOFF", QSerialPort.SoftwareControl)

    def fill_ports_info(self):
        self.m_ui.serialPortInfoListBox.clear()
        for info in QSerialPortInfo.availablePorts():
            list = []
            description = info.description()
            manufacturer = info.manufacturer()
            serial_number = info.serialNumber()
            list.append(info.portName())
            list.append(description if description else BLANK_STRING)
            list.append(manufacturer if manufacturer else BLANK_STRING)
            list.append(serial_number if serial_number else BLANK_STRING)
            list.append(info.systemLocation())
            vid = info.vendorIdentifier()
            list.append(f"{vid:x}" if vid else BLANK_STRING)
            pid = info.productIdentifier()
            list.append(f"{pid:x}" if pid else BLANK_STRING)
            self.m_ui.serialPortInfoListBox.addItem(list[0], list)

        self._custom_port_index = self.m_ui.serialPortInfoListBox.count()
        self.m_ui.serialPortInfoListBox.addItem("Custom")

    def update_settings(self):
        self.m_currentSettings.name = self.m_ui.serialPortInfoListBox.currentText()

        baud_index = self.m_ui.baudRateBox.currentIndex()
        if baud_index == CUSTOM_BAUDRATE_INDEX:
            text = self.m_ui.baudRateBox.currentText()
            self.m_currentSettings.baud_rate = int(text)
        else:
            self.m_currentSettings.baud_rate = self.m_ui.baudRateBox.currentData()
        self.m_currentSettings.string_baud_rate = f"{self.m_currentSettings.baud_rate}"

        self.m_currentSettings.data_bits = self.m_ui.dataBitsBox.currentData()
        self.m_currentSettings.string_data_bits = self.m_ui.dataBitsBox.currentText()

        self.m_currentSettings.parity = self.m_ui.parityBox.currentData()
        self.m_currentSettings.string_parity = self.m_ui.parityBox.currentText()

        self.m_currentSettings.stop_bits = self.m_ui.stopBitsBox.currentData()
        self.m_currentSettings.string_stop_bits = self.m_ui.stopBitsBox.currentText()

        self.m_currentSettings.flow_control = self.m_ui.flowControlBox.currentData()
        self.m_currentSettings.string_flow_control = self.m_ui.flowControlBox.currentText()

        self.m_currentSettings.local_echo_enabled = self.m_ui.localEchoCheckBox.isChecked()
