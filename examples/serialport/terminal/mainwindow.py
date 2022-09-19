# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QIODeviceBase, Slot
from PySide6.QtWidgets import QLabel, QMainWindow, QMessageBox
from PySide6.QtSerialPort import QSerialPort

from ui_mainwindow import Ui_MainWindow
from console import Console
from settingsdialog import SettingsDialog


HELP = """The <b>Simple Terminal</b> example demonstrates how to
 use the Qt Serial Port module in modern GUI applications
 using Qt, with a menu bar, toolbars, and a status bar."""


def description(s):
    return (f"Connected to {s.name} : {s.string_baud_rate}, "
            f"{s.string_data_bits}, {s.string_parity}, {s.string_stop_bits}, "
            f"{s.string_flow_control}")


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_ui = Ui_MainWindow()
        self.m_status = QLabel()
        self.m_console = Console()
        self.m_settings = SettingsDialog(self)
        self.m_serial = QSerialPort(self)
        self.m_ui.setupUi(self)
        self.m_console.setEnabled(False)
        self.setCentralWidget(self.m_console)

        self.m_ui.actionConnect.setEnabled(True)
        self.m_ui.actionDisconnect.setEnabled(False)
        self.m_ui.actionQuit.setEnabled(True)
        self.m_ui.actionConfigure.setEnabled(True)

        self.m_ui.statusBar.addWidget(self.m_status)

        self.m_ui.actionConnect.triggered.connect(self.open_serial_port)
        self.m_ui.actionDisconnect.triggered.connect(self.close_serial_port)
        self.m_ui.actionQuit.triggered.connect(self.close)
        self.m_ui.actionConfigure.triggered.connect(self.m_settings.show)
        self.m_ui.actionClear.triggered.connect(self.m_console.clear)
        self.m_ui.actionAbout.triggered.connect(self.about)
        self.m_ui.actionAboutQt.triggered.connect(qApp.aboutQt)

        self.m_serial.errorOccurred.connect(self.handle_error)
        self.m_serial.readyRead.connect(self.read_data)
        self.m_console.get_data.connect(self.write_data)

    @Slot()
    def open_serial_port(self):
        s = self.m_settings.settings()
        self.m_serial.setPortName(s.name)
        self.m_serial.setBaudRate(s.baud_rate)
        self.m_serial.setDataBits(s.data_bits)
        self.m_serial.setParity(s.parity)
        self.m_serial.setStopBits(s.stop_bits)
        self.m_serial.setFlowControl(s.flow_control)
        if self.m_serial.open(QIODeviceBase.ReadWrite):
            self.m_console.setEnabled(True)
            self.m_console.set_local_echo_enabled(s.local_echo_enabled)
            self.m_ui.actionConnect.setEnabled(False)
            self.m_ui.actionDisconnect.setEnabled(True)
            self.m_ui.actionConfigure.setEnabled(False)
            self.show_status_message(description(s))
        else:
            QMessageBox.critical(self, "Error", self.m_serial.errorString())
            self.show_status_message("Open error")

    @Slot()
    def close_serial_port(self):
        if self.m_serial.isOpen():
            self.m_serial.close()
        self.m_console.setEnabled(False)
        self.m_ui.actionConnect.setEnabled(True)
        self.m_ui.actionDisconnect.setEnabled(False)
        self.m_ui.actionConfigure.setEnabled(True)
        self.show_status_message("Disconnected")

    @Slot()
    def about(self):
        QMessageBox.about(self, "About Simple Terminal", HELP)

    @Slot(bytearray)
    def write_data(self, data):
        self.m_serial.write(data)

    @Slot()
    def read_data(self):
        data = self.m_serial.readAll()
        self.m_console.put_data(data.data())

    @Slot(QSerialPort.SerialPortError)
    def handle_error(self, error):
        if error == QSerialPort.ResourceError:
            QMessageBox.critical(self, "Critical Error",
                                 self.m_serial.errorString())
            self.close_serial_port()

    @Slot(str)
    def show_status_message(self, message):
        self.m_status.setText(message)
