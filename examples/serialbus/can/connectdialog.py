# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QSettings, Qt, Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog
from PySide6.QtSerialBus import QCanBus, QCanBusDevice

from ui_connectdialog import Ui_ConnectDialog


class Settings():
    def __init__(self):
        self.plugin_name = ""
        self.device_interface_name = ""
        self.configurations = []
        self.use_configuration_enabled = False
        self.use_model_ring_buffer = True
        self.model_ring_buffer_size = 1000
        self.use_autoscroll = False


class ConnectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_ui = Ui_ConnectDialog()
        self.m_currentSettings = Settings()
        self.m_interfaces = []
        self.m_settings = QSettings("QtProject", "CAN example")
        self.m_ui.setupUi(self)

        self.m_ui.errorFilterEdit.setValidator(QIntValidator(0, 0x1FFFFFFF, self))

        self.m_ui.loopbackBox.addItem("unspecified")
        self.m_ui.loopbackBox.addItem("False", False)
        self.m_ui.loopbackBox.addItem("True", True)

        self.m_ui.receiveOwnBox.addItem("unspecified")
        self.m_ui.receiveOwnBox.addItem("False", False)
        self.m_ui.receiveOwnBox.addItem("True", True)

        self.m_ui.canFdBox.addItem("False", False)
        self.m_ui.canFdBox.addItem("True", True)

        self.m_ui.dataBitrateBox.set_flexible_date_rate_enabled(True)

        self.m_ui.okButton.clicked.connect(self.ok)
        self.m_ui.cancelButton.clicked.connect(self.cancel)
        self.m_ui.useConfigurationBox.toggled.connect(self.m_ui.configurationBox.setEnabled)
        self.m_ui.pluginListBox.currentTextChanged.connect(self.plugin_changed)
        self.m_ui.interfaceListBox.currentTextChanged.connect(self.interface_changed)
        self.m_ui.ringBufferBox.checkStateChanged.connect(self._ring_buffer_changed)

        self.m_ui.rawFilterEdit.hide()
        self.m_ui.rawFilterLabel.hide()

        self.m_ui.pluginListBox.addItems(QCanBus.instance().plugins())

        self.restore_settings()

    @Slot(int)
    def _ring_buffer_changed(self, state):
        self.m_ui.ringBufferLimitBox.setEnabled(state == Qt.CheckState.Checked)

    def settings(self):
        return self.m_currentSettings

    def save_settings(self):
        qs = self.m_settings
        cur = self.m_currentSettings
        qs.beginGroup("LastSettings")
        qs.setValue("PluginName", self.m_currentSettings.plugin_name)
        qs.setValue("DeviceInterfaceName", cur.device_interface_name)
        qs.setValue("UseAutoscroll", cur.use_autoscroll)
        qs.setValue("UseRingBuffer", cur.use_model_ring_buffer)
        qs.setValue("RingBufferSize", cur.model_ring_buffer_size)
        qs.setValue("UseCustomConfiguration", cur.use_configuration_enabled)

        if cur.use_configuration_enabled:
            qs.setValue("Loopback",
                        self.configuration_value(QCanBusDevice.LoopbackKey))
            qs.setValue("ReceiveOwn",
                        self.configuration_value(QCanBusDevice.ReceiveOwnKey))
            qs.setValue("ErrorFilter",
                        self.configuration_value(QCanBusDevice.ErrorFilterKey))
            qs.setValue("BitRate",
                        self.configuration_value(QCanBusDevice.BitRateKey))
            qs.setValue("CanFd",
                        self.configuration_value(QCanBusDevice.CanFdKey))
            qs.setValue("DataBitRate",
                        self.configuration_value(QCanBusDevice.DataBitRateKey))
        qs.endGroup()

    def restore_settings(self):
        qs = self.m_settings
        cur = self.m_currentSettings
        qs.beginGroup("LastSettings")
        cur.plugin_name = qs.value("PluginName", "", str)
        cur.device_interface_name = qs.value("DeviceInterfaceName", "", str)
        cur.use_autoscroll = qs.value("UseAutoscroll", False, bool)
        cur.use_model_ring_buffer = qs.value("UseRingBuffer", False, bool)
        cur.model_ring_buffer_size = qs.value("RingBufferSize", 0, int)
        cur.use_configuration_enabled = qs.value("UseCustomConfiguration", False, bool)

        self.revert_settings()

        if cur.use_configuration_enabled:
            self.m_ui.loopbackBox.setCurrentText(qs.value("Loopback"))
            self.m_ui.receiveOwnBox.setCurrentText(qs.value("ReceiveOwn"))
            self.m_ui.errorFilterEdit.setText(qs.value("ErrorFilter"))
            self.m_ui.bitrateBox.setCurrentText(qs.value("BitRate"))
            self.m_ui.canFdBox.setCurrentText(qs.value("CanFd"))
            self.m_ui.dataBitrateBox.setCurrentText(qs.value("DataBitRate"))

        qs.endGroup()
        self.update_settings()

    @Slot(str)
    def plugin_changed(self, plugin):
        self.m_ui.interfaceListBox.clear()
        interfaces, error_string = QCanBus.instance().availableDevices(plugin)
        self.m_interfaces = interfaces
        for info in self.m_interfaces:
            self.m_ui.interfaceListBox.addItem(info.name())

    @Slot(str)
    def interface_changed(self, interface):
        for info in self.m_interfaces:
            if interface == info.name():
                self.m_ui.deviceInfoBox.set_device_info(info)
                return
        self.m_ui.deviceInfoBox.clear()

    @Slot()
    def ok(self):
        self.update_settings()
        self.save_settings()
        self.accept()

    @Slot()
    def cancel(self):
        self.revert_settings()
        self.reject()

    def configuration_value(self, key):
        result = None
        for k, v in self.m_currentSettings.configurations:
            if k == key:
                result = v
                break
        if not result and (key == QCanBusDevice.LoopbackKey or key == QCanBusDevice.ReceiveOwnKey):
            return "unspecified"
        return str(result)

    def revert_settings(self):
        self.m_ui.pluginListBox.setCurrentText(self.m_currentSettings.plugin_name)
        self.m_ui.interfaceListBox.setCurrentText(self.m_currentSettings.device_interface_name)
        self.m_ui.useConfigurationBox.setChecked(self.m_currentSettings.use_configuration_enabled)

        self.m_ui.ringBufferBox.setChecked(self.m_currentSettings.use_model_ring_buffer)
        self.m_ui.ringBufferLimitBox.setValue(self.m_currentSettings.model_ring_buffer_size)
        self.m_ui.autoscrollBox.setChecked(self.m_currentSettings.use_autoscroll)

        value = self.configuration_value(QCanBusDevice.LoopbackKey)
        self.m_ui.loopbackBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.ReceiveOwnKey)
        self.m_ui.receiveOwnBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.ErrorFilterKey)
        self.m_ui.errorFilterEdit.setText(value)

        value = self.configuration_value(QCanBusDevice.BitRateKey)
        self.m_ui.bitrateBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.CanFdKey)
        self.m_ui.canFdBox.setCurrentText(value)

        value = self.configuration_value(QCanBusDevice.DataBitRateKey)
        self.m_ui.dataBitrateBox.setCurrentText(value)

    def update_settings(self):
        self.m_currentSettings.plugin_name = self.m_ui.pluginListBox.currentText()
        self.m_currentSettings.device_interface_name = self.m_ui.interfaceListBox.currentText()
        self.m_currentSettings.use_configuration_enabled = self.m_ui.useConfigurationBox.isChecked()

        self.m_currentSettings.use_model_ring_buffer = self.m_ui.ringBufferBox.isChecked()
        self.m_currentSettings.model_ring_buffer_size = self.m_ui.ringBufferLimitBox.value()
        self.m_currentSettings.use_autoscroll = self.m_ui.autoscrollBox.isChecked()

        if self.m_currentSettings.use_configuration_enabled:
            self.m_currentSettings.configurations.clear()
            # process LoopBack
            if self.m_ui.loopbackBox.currentIndex() != 0:
                item = (QCanBusDevice.LoopbackKey, self.m_ui.loopbackBox.currentData())
                self.m_currentSettings.configurations.append(item)

            # process ReceiveOwnKey
            if self.m_ui.receiveOwnBox.currentIndex() != 0:
                item = (QCanBusDevice.ReceiveOwnKey, self.m_ui.receiveOwnBox.currentData())
                self.m_currentSettings.configurations.append(item)

            # process error filter
            error_filter = self.m_ui.errorFilterEdit.text()
            if error_filter:
                ok = False
                try:
                    int(error_filter)  # check if value contains a valid integer
                    ok = True
                except ValueError:
                    pass
                if ok:
                    item = (QCanBusDevice.ErrorFilterKey, error_filter)
                    self.m_currentSettings.configurations.append(item)

            # process raw filter list
            if self.m_ui.rawFilterEdit.text():
                pass  # TODO current ui not sufficient to reflect this param

            # process bitrate
            bitrate = self.m_ui.bitrateBox.bit_rate()
            if bitrate > 0:
                item = (QCanBusDevice.BitRateKey, bitrate)
                self.m_currentSettings.configurations.append(item)

            # process CAN FD setting
            fd_item = (QCanBusDevice.CanFdKey, self.m_ui.canFdBox.currentData())
            self.m_currentSettings.configurations.append(fd_item)

            # process data bitrate
            data_bitrate = self.m_ui.dataBitrateBox.bit_rate()
            if data_bitrate > 0:
                item = (QCanBusDevice.DataBitRateKey, data_bitrate)
                self.m_currentSettings.configurations.append(item)
