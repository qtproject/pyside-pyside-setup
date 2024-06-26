# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import IntEnum

from PySide6.QtCore import QUrl, Slot
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMainWindow
from PySide6.QtSerialBus import (QModbusDataUnit, QModbusDevice,
                                 QModbusRtuSerialClient, QModbusTcpClient)

from ui_mainwindow import Ui_MainWindow
from settingsdialog import SettingsDialog
from writeregistermodel import WriteRegisterModel


class ModbusConnection(IntEnum):
    SERIAL = 0
    TCP = 1


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._modbus_device = None

        self._settings_dialog = SettingsDialog(self)

        self.init_actions()

        self._write_model = WriteRegisterModel(self)
        self._write_model.set_start_address(self.ui.writeAddress.value())
        self._write_model.set_number_of_values(self.ui.writeSize.currentText())

        self.ui.writeValueTable.setModel(self._write_model)
        self.ui.writeValueTable.hideColumn(2)
        vp = self.ui.writeValueTable.viewport()
        self._write_model.update_viewport.connect(vp.update)

        self.ui.writeTable.addItem("Coils", QModbusDataUnit.Coils)
        self.ui.writeTable.addItem("Discrete Inputs", QModbusDataUnit.DiscreteInputs)
        self.ui.writeTable.addItem("Input Registers", QModbusDataUnit.InputRegisters)
        self.ui.writeTable.addItem("Holding Registers", QModbusDataUnit.HoldingRegisters)

        self.ui.connectType.setCurrentIndex(0)
        self.onConnectTypeChanged(0)

        self._write_size_model = QStandardItemModel(0, 1, self)
        for i in range(1, 11):
            self._write_size_model.appendRow(QStandardItem(f"{i}"))
        self.ui.writeSize.setModel(self._write_size_model)
        self.ui.writeSize.setCurrentText("10")
        self.ui.writeSize.currentTextChanged.connect(self._write_model.set_number_of_values)

        self.ui.writeAddress.valueChanged.connect(self._write_model.set_start_address)
        self.ui.writeAddress.valueChanged.connect(self._writeAddress)

    @Slot(int)
    def _writeAddress(self, i):
        last_possible_index = 0
        currentIndex = self.ui.writeSize.currentIndex()
        for ii in range(0, 10):
            if ii < (10 - i):
                last_possible_index = ii
                self._write_size_model.item(ii).setEnabled(True)
            else:
                self._write_size_model.item(ii).setEnabled(False)
        if currentIndex > last_possible_index:
            self.ui.writeSize.setCurrentIndex(last_possible_index)

    def _close_device(self):
        if self._modbus_device:
            self._modbus_device.disconnectDevice()
            del self._modbus_device
            self._modbus_device = None

    def closeEvent(self, event):
        self._close_device()
        event.accept()

    def init_actions(self):
        self.ui.actionConnect.setEnabled(True)
        self.ui.actionDisconnect.setEnabled(False)
        self.ui.actionExit.setEnabled(True)
        self.ui.actionOptions.setEnabled(True)

        self.ui.connectButton.clicked.connect(self.onConnectButtonClicked)
        self.ui.actionConnect.triggered.connect(self.onConnectButtonClicked)
        self.ui.actionDisconnect.triggered.connect(self.onConnectButtonClicked)
        self.ui.readButton.clicked.connect(self.onReadButtonClicked)
        self.ui.writeButton.clicked.connect(self.onWriteButtonClicked)
        self.ui.readWriteButton.clicked.connect(self.onReadWriteButtonClicked)
        self.ui.connectType.currentIndexChanged.connect(self.onConnectTypeChanged)
        self.ui.writeTable.currentIndexChanged.connect(self.onWriteTableChanged)

        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionOptions.triggered.connect(self._settings_dialog.show)

    @Slot(int)
    def onConnectTypeChanged(self, index):
        self._close_device()

        if index == ModbusConnection.SERIAL:
            self._modbus_device = QModbusRtuSerialClient(self)
        elif index == ModbusConnection.TCP:
            self._modbus_device = QModbusTcpClient(self)
            if not self.ui.portEdit.text():
                self.ui.portEdit.setText("127.0.0.1:50200")

        self._modbus_device.errorOccurred.connect(self._show_device_errorstring)

        if not self._modbus_device:
            self.ui.connectButton.setDisabled(True)
            message = "Could not create Modbus client."
            self.statusBar().showMessage(message, 5000)
        else:
            self._modbus_device.stateChanged.connect(self.onModbusStateChanged)

    @Slot()
    def _show_device_errorstring(self):
        self.statusBar().showMessage(self._modbus_device.errorString(), 5000)

    @Slot()
    def onConnectButtonClicked(self):
        if not self._modbus_device:
            return

        self.statusBar().clearMessage()
        md = self._modbus_device
        if md.state() != QModbusDevice.ConnectedState:
            settings = self._settings_dialog.settings()
            if self.ui.connectType.currentIndex() == ModbusConnection.SERIAL:
                md.setConnectionParameter(QModbusDevice.SerialPortNameParameter,
                                          self.ui.portEdit.text())
                md.setConnectionParameter(QModbusDevice.SerialParityParameter,
                                          settings.parity)
                md.setConnectionParameter(QModbusDevice.SerialBaudRateParameter,
                                          settings.baud)
                md.setConnectionParameter(QModbusDevice.SerialDataBitsParameter,
                                          settings.data_bits)
                md.setConnectionParameter(QModbusDevice.SerialStopBitsParameter,
                                          settings.stop_bits)
            else:
                url = QUrl.fromUserInput(self.ui.portEdit.text())
                md.setConnectionParameter(QModbusDevice.NetworkPortParameter,
                                          url.port())
                md.setConnectionParameter(QModbusDevice.NetworkAddressParameter,
                                          url.host())

            md.setTimeout(settings.response_time)
            md.setNumberOfRetries(settings.number_of_retries)
            if not md.connectDevice():
                message = "Connect failed: " + md.errorString()
                self.statusBar().showMessage(message, 5000)
            else:
                self.ui.actionConnect.setEnabled(False)
                self.ui.actionDisconnect.setEnabled(True)

        else:
            md.disconnectDevice()
            self.ui.actionConnect.setEnabled(True)
            self.ui.actionDisconnect.setEnabled(False)

    @Slot(int)
    def onModbusStateChanged(self, state):
        connected = (state != QModbusDevice.UnconnectedState)
        self.ui.actionConnect.setEnabled(not connected)
        self.ui.actionDisconnect.setEnabled(connected)

        if state == QModbusDevice.UnconnectedState:
            self.ui.connectButton.setText("Connect")
        elif state == QModbusDevice.ConnectedState:
            self.ui.connectButton.setText("Disconnect")

    @Slot()
    def onReadButtonClicked(self):
        if not self._modbus_device:
            return
        self.ui.readValue.clear()
        self.statusBar().clearMessage()
        reply = self._modbus_device.sendReadRequest(self.read_request(),
                                                    self.ui.serverEdit.value())
        if reply:
            if not reply.isFinished():
                reply.finished.connect(self.onReadReady)
            else:
                del reply  # broadcast replies return immediately
        else:
            message = "Read error: " + self._modbus_device.errorString()
            self.statusBar().showMessage(message, 5000)

    @Slot()
    def onReadReady(self):
        reply = self.sender()
        if not reply:
            return

        if reply.error() == QModbusDevice.NoError:
            unit = reply.result()
            total = unit.valueCount()
            for i in range(0, total):
                addr = unit.startAddress() + i
                value = unit.value(i)
                if unit.registerType().value <= QModbusDataUnit.Coils.value:
                    entry = f"Address: {addr}, Value: {value}"
                else:
                    entry = f"Address: {addr}, Value: {value:x}"
                self.ui.readValue.addItem(entry)

        elif reply.error() == QModbusDevice.ProtocolError:
            e = reply.errorString()
            ex = reply.rawResult().exceptionCode()
            message = f"Read response error: {e} (Modbus exception: 0x{ex:x})"
            self.statusBar().showMessage(message, 5000)
        else:
            e = reply.errorString()
            code = int(reply.error())
            message = f"Read response error: {e} (code: 0x{code:x})"
            self.statusBar().showMessage(message, 5000)

        reply.deleteLater()

    @Slot()
    def onWriteButtonClicked(self):
        if not self._modbus_device:
            return
        self.statusBar().clearMessage()

        write_unit = self.write_request()
        total = write_unit.valueCount()
        table = write_unit.registerType()
        for i in range(0, total):
            addr = i + write_unit.startAddress()
            if table == QModbusDataUnit.Coils:
                write_unit.setValue(i, self._write_model.m_coils[addr])
            else:
                write_unit.setValue(i, self._write_model.m_holdingRegisters[addr])

        reply = self._modbus_device.sendWriteRequest(write_unit,
                                                     self.ui.serverEdit.value())
        if reply:
            if reply.isFinished():
                # broadcast replies return immediately
                reply.deleteLater()
            else:
                reply.finished.connect(self._write_finished)
        else:
            message = "Write error: " + self._modbus_device.errorString()
            self.statusBar().showMessage(message, 5000)

    @Slot()
    def _write_finished(self):
        reply = self.sender()
        if not reply:
            return
        error = reply.error()
        if error == QModbusDevice.ProtocolError:
            e = reply.errorString()
            ex = reply.rawResult().exceptionCode()
            message = f"Write response error: {e} (Modbus exception: 0x{ex:x}"
            self.statusBar().showMessage(message, 5000)
        elif error != QModbusDevice.NoError:
            e = reply.errorString()
            message = f"Write response error: {e} (code: 0x{error:x})"
            self.statusBar().showMessage(message, 5000)
        reply.deleteLater()

    @Slot()
    def onReadWriteButtonClicked(self):
        if not self._modbus_device:
            return
        self.ui.readValue.clear()
        self.statusBar().clearMessage()

        write_unit = self.write_request()
        table = write_unit.registerType()
        total = write_unit.valueCount()
        for i in range(0, total):
            addr = i + write_unit.startAddress()
            if table == QModbusDataUnit.Coils:
                write_unit.setValue(i, self._write_model.m_coils[addr])
            else:
                write_unit.setValue(i, self._write_model.m_holdingRegisters[addr])

        reply = self._modbus_device.sendReadWriteRequest(self.read_request(),
                                                         write_unit,
                                                         self.ui.serverEdit.value())
        if reply:
            if not reply.isFinished():
                reply.finished.connect(self.onReadReady)
            else:
                del reply  # broadcast replies return immediately
        else:
            message = "Read error: " + self._modbus_device.errorString()
            self.statusBar().showMessage(message, 5000)

    @Slot(int)
    def onWriteTableChanged(self, index):
        coils_or_holding = index == 0 or index == 3
        if coils_or_holding:
            self.ui.writeValueTable.setColumnHidden(1, index != 0)
            self.ui.writeValueTable.setColumnHidden(2, index != 3)
            self.ui.writeValueTable.resizeColumnToContents(0)

        self.ui.readWriteButton.setEnabled(index == 3)
        self.ui.writeButton.setEnabled(coils_or_holding)
        self.ui.writeGroupBox.setEnabled(coils_or_holding)

    def read_request(self):
        table = self.ui.writeTable.currentData()

        start_address = self.ui.readAddress.value()
        assert start_address >= 0 and start_address < 10

        # do not go beyond 10 entries
        number_of_entries = min(int(self.ui.readSize.currentText()),
                                10 - start_address)
        return QModbusDataUnit(table, start_address, number_of_entries)

    def write_request(self):
        table = self.ui.writeTable.currentData()

        start_address = self.ui.writeAddress.value()
        assert start_address >= 0 and start_address < 10

        # do not go beyond 10 entries
        number_of_entries = min(int(self.ui.writeSize.currentText()),
                                10 - start_address)
        return QModbusDataUnit(table, start_address, number_of_entries)
