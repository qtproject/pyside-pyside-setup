# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QTimer, QUrl, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QMainWindow
from PySide6.QtSerialBus import QCanBus, QCanBusDevice, QCanBusFrame

from connectdialog import ConnectDialog
from canbusdeviceinfodialog import CanBusDeviceInfoDialog
from ui_mainwindow import Ui_MainWindow
from receivedframesmodel import ReceivedFramesModel


def frame_flags(frame):
    result = " --- "
    if frame.hasBitrateSwitch():
        result[1] = 'B'
    if frame.hasErrorStateIndicator():
        result[2] = 'E'
    if frame.hasLocalEcho():
        result[3] = 'L'
    return result


def show_help():
    url = "http://doc.qt.io/qt-6/qtcanbus-backends.html#can-bus-plugins"
    QDesktopServices.openUrl(QUrl(url))


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_ui = Ui_MainWindow()
        self.m_number_frames_written = 0
        self.m_number_frames_received = 0
        self.m_written = None
        self.m_received = None
        self.m_can_device = None

        self.m_busStatusTimer = QTimer(self)

        self.m_ui.setupUi(self)
        self.m_connect_dialog = ConnectDialog(self)

        self.m_status = QLabel()
        self.m_ui.statusBar.addPermanentWidget(self.m_status)
        self.m_written = QLabel()
        self.m_ui.statusBar.addWidget(self.m_written)
        self.m_received = QLabel()
        self.m_ui.statusBar.addWidget(self.m_received)

        self.m_model = ReceivedFramesModel(self)
        self.m_model.set_queue_limit(1000)
        self.m_ui.receivedFramesView.set_model(self.m_model)

        self.init_actions_connections()
        QTimer.singleShot(50, self.m_connect_dialog.show)

        self.m_busStatusTimer.timeout.connect(self.bus_status)
        self.m_appendTimer = QTimer(self)
        self.m_appendTimer.timeout.connect(self.onAppendFramesTimeout)
        self.m_appendTimer.start(350)

    def init_actions_connections(self):
        self.m_ui.actionDisconnect.setEnabled(False)
        self.m_ui.actionDeviceInformation.setEnabled(False)
        self.m_ui.sendFrameBox.setEnabled(False)

        self.m_ui.sendFrameBox.send_frame.connect(self.send_frame)
        self.m_ui.actionConnect.triggered.connect(self._action_connect)
        self.m_connect_dialog.accepted.connect(self.connect_device)
        self.m_ui.actionDisconnect.triggered.connect(self.disconnect_device)
        self.m_ui.actionResetController.triggered.connect(self._reset_controller)
        self.m_ui.actionQuit.triggered.connect(self.close)
        self.m_ui.actionAboutQt.triggered.connect(qApp.aboutQt)  # noqa: F821
        self.m_ui.actionClearLog.triggered.connect(self.m_model.clear)
        self.m_ui.actionPluginDocumentation.triggered.connect(show_help)
        self.m_ui.actionDeviceInformation.triggered.connect(self._action_device_information)

    @Slot()
    def _action_connect(self):
        if self.m_can_device:
            self.m_can_device.deleteLater()
            self.m_can_device = None
        self.m_connect_dialog.show()

    @Slot()
    def _reset_controller(self):
        self.m_can_device.resetController()

    @Slot()
    def _action_device_information(self):
        info = self.m_can_device.deviceInfo()
        dialog = CanBusDeviceInfoDialog(info, self)
        dialog.exec()

    @Slot(QCanBusDevice.CanBusError)
    def process_errors(self, error):
        if error != QCanBusDevice.NoError:
            self.m_status.setText(self.m_can_device.errorString())

    @Slot()
    def connect_device(self):
        p = self.m_connect_dialog.settings()
        if p.use_model_ring_buffer:
            self.m_model.set_queue_limit(p.model_ring_buffer_size)
        else:
            self.m_model.set_queue_limit(0)

        device, error_string = QCanBus.instance().createDevice(
            p.plugin_name, p.device_interface_name)
        if not device:
            self.m_status.setText(
                f"Error creating device '{p.plugin_name}', reason: '{error_string}'")
            return

        self.m_number_frames_written = 0
        self.m_can_device = device
        self.m_can_device.errorOccurred.connect(self.process_errors)
        self.m_can_device.framesReceived.connect(self.process_received_frames)
        self.m_can_device.framesWritten.connect(self.process_frames_written)

        if p.use_configuration_enabled:
            for k, v in p.configurations:
                self.m_can_device.setConfigurationParameter(k, v)

        if not self.m_can_device.connectDevice():
            e = self.m_can_device.errorString()
            self.m_status.setText(f"Connection error: {e}")
            self.m_can_device = None
        else:
            self.m_ui.actionConnect.setEnabled(False)
            self.m_ui.actionDisconnect.setEnabled(True)
            self.m_ui.actionDeviceInformation.setEnabled(True)
            self.m_ui.sendFrameBox.setEnabled(True)
            config_bit_rate = self.m_can_device.configurationParameter(QCanBusDevice.BitRateKey)
            if config_bit_rate is not None and config_bit_rate > 0:
                is_can_fd = bool(self.m_can_device.configurationParameter(QCanBusDevice.CanFdKey))
                config_data_bit_rate = self.m_can_device.configurationParameter(
                    QCanBusDevice.DataBitRateKey)
                bit_rate = config_bit_rate / 1000
                if is_can_fd and config_data_bit_rate > 0:
                    data_bit_rate = config_data_bit_rate / 1000
                    m = (f"Plugin: {p.plugin_name}, connected to {p.device_interface_name} "
                         f"at {bit_rate} / {data_bit_rate} kBit/s")
                    self.m_status.setText(m)
                else:
                    m = (f"Plugin: {p.plugin_name}, connected to {p.device_interface_name} "
                         f"at {bit_rate} kBit/s")
                    self.m_status.setText(m)

            else:
                self.m_status.setText(
                    f"Plugin: {p.plugin_name}, connected to {p.device_interface_name}")

            if self.m_can_device.hasBusStatus():
                self.m_busStatusTimer.start(2000)
            else:
                self.m_ui.busStatus.setText("No CAN bus status available.")

    def bus_status(self):
        if not self.m_can_device or not self.m_can_device.hasBusStatus():
            self.m_ui.busStatus.setText("No CAN bus status available.")
            self.m_busStatusTimer.stop()
            return

        state = self.m_can_device.busStatus()
        if state == QCanBusDevice.CanBusStatus.Good:
            self.m_ui.busStatus.setText("CAN bus status: Good.")
        elif state == QCanBusDevice.CanBusStatus.Warning:
            self.m_ui.busStatus.setText("CAN bus status: Warning.")
        elif state == QCanBusDevice.CanBusStatus.Error:
            self.m_ui.busStatus.setText("CAN bus status: Error.")
        elif state == QCanBusDevice.CanBusStatus.BusOff:
            self.m_ui.busStatus.setText("CAN bus status: Bus Off.")
        else:
            self.m_ui.busStatus.setText("CAN bus status: Unknown.")

    @Slot()
    def disconnect_device(self):
        if not self.m_can_device:
            return
        self.m_busStatusTimer.stop()
        self.m_can_device.disconnectDevice()
        self.m_ui.actionConnect.setEnabled(True)
        self.m_ui.actionDisconnect.setEnabled(False)
        self.m_ui.actionDeviceInformation.setEnabled(False)
        self.m_ui.sendFrameBox.setEnabled(False)
        self.m_status.setText("Disconnected")

    @Slot(int)
    def process_frames_written(self, count):
        self.m_number_frames_written += count
        self.m_written.setText(f"{self.m_number_frames_written} frames written")

    def closeEvent(self, event):
        self.m_connect_dialog.close()
        event.accept()

    @Slot()
    def process_received_frames(self):
        if not self.m_can_device:
            return
        while self.m_can_device.framesAvailable():
            self.m_number_frames_received = self.m_number_frames_received + 1
            frame = self.m_can_device.readFrame()
            data = ""
            if frame.frameType() == QCanBusFrame.ErrorFrame:
                data = self.m_can_device.interpretErrorFrame(frame)
            else:
                data = frame.payload().toHex(' ').toUpper()

            secs = frame.timeStamp().seconds()
            microsecs = frame.timeStamp().microSeconds() / 100
            time = f"{secs:>10}.{microsecs:0>4}"
            flags = frame_flags(frame)

            id = f"{frame.frameId():x}"
            dlc = f"{frame.payload().size()}"
            frame = [f"{self.m_number_frames_received}", time, flags, id, dlc, data]
            self.m_model.append_frame(frame)

    @Slot(QCanBusFrame)
    def send_frame(self, frame):
        if self.m_can_device:
            self.m_can_device.writeFrame(frame)

    @Slot()
    def onAppendFramesTimeout(self):
        if not self.m_can_device:
            return
        if self.m_model.need_update():
            self.m_model.update()
            if self.m_connect_dialog.settings().use_autoscroll:
                self.m_ui.receivedFramesView.scrollToBottom()
            self.m_received.setText(f"{self.m_number_frames_received} frames received")
