# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QPoint, Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QListWidgetItem, QListWidget, QMenu
from PySide6.QtBluetooth import (QBluetoothAddress, QBluetoothDeviceDiscoveryAgent,
                                 QBluetoothDeviceInfo, QBluetoothLocalDevice)

from ui_device import Ui_DeviceDiscovery
from service import ServiceDiscoveryDialog


class DeviceDiscoveryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._local_device = QBluetoothLocalDevice()
        self._ui = Ui_DeviceDiscovery()
        self._ui.setupUi(self)
        # In case of multiple Bluetooth adapters it is possible to set adapter
        # which will be used. Example code:
        #
        # address = QBluetoothAddress("XX:XX:XX:XX:XX:XX")
        # discoveryAgent = QBluetoothDeviceDiscoveryAgent(address)

        self._discovery_agent = QBluetoothDeviceDiscoveryAgent()

        self._ui.scan.clicked.connect(self.start_scan)
        self._discovery_agent.deviceDiscovered.connect(self.add_device)
        self._discovery_agent.finished.connect(self.scan_finished)
        self._ui.list.itemActivated.connect(self.item_activated)
        self._local_device.hostModeStateChanged.connect(self.host_mode_state_changed)

        self.host_mode_state_changed(self._local_device.hostMode())
        # add context menu for devices to be able to pair device
        self._ui.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._ui.list.customContextMenuRequested.connect(self.display_pairing_menu)
        self._local_device.pairingFinished.connect(self.pairing_done)

    @Slot(QBluetoothDeviceInfo)
    def add_device(self, info):
        a = info.address().toString()
        label = f"{a} {info.name()}"
        items = self._ui.list.findItems(label, Qt.MatchExactly)
        if not items:
            item = QListWidgetItem(label)
            pairing_status = self._local_device.pairingStatus(info.address())
            if (pairing_status == QBluetoothLocalDevice.Paired
                or pairing_status == QBluetoothLocalDevice.AuthorizedPaired):
                item.setForeground(QColor(Qt.green))
            else:
                item.setForeground(QColor(Qt.black))
            self._ui.list.addItem(item)

    @Slot()
    def start_scan(self):
        self._discovery_agent.start()
        self._ui.scan.setEnabled(False)

    @Slot()
    def scan_finished(self):
        self._ui.scan.setEnabled(True)

    @Slot(QListWidgetItem)
    def item_activated(self, item):
        text = item.text()
        index = text.find(' ')
        if index == -1:
            return

        address = QBluetoothAddress(text[0:index])
        name = text[index + 1:]

        d = ServiceDiscoveryDialog(name, address)
        d.exec()

    @Slot(bool)
    def on_discoverable_clicked(self, clicked):
        if clicked:
            self._local_device.setHostMode(QBluetoothLocalDevice.HostDiscoverable)
        else:
            self._local_device.setHostMode(QBluetoothLocalDevice.HostConnectable)

    @Slot(bool)
    def on_power_clicked(self, clicked):
        if clicked:
            self._local_device.powerOn()
        else:
            self._local_device.setHostMode(QBluetoothLocalDevice.HostPoweredOff)

    @Slot("QBluetoothLocalDevice::HostMode")
    def host_mode_state_changed(self, mode):
        self._ui.power.setChecked(mode != QBluetoothLocalDevice.HostPoweredOff)
        self._ui.discoverable.setChecked(mode == QBluetoothLocalDevice.HostDiscoverable)

        on = mode != QBluetoothLocalDevice.HostPoweredOff
        self._ui.scan.setEnabled(on)
        self._ui.discoverable.setEnabled(on)

    @Slot(QPoint)
    def display_pairing_menu(self, pos):
        if self._ui.list.count() == 0:
            return
        menu = QMenu(self)
        pair_action = menu.addAction("Pair")
        remove_pair_action = menu.addAction("Remove Pairing")
        chosen_action = menu.exec(self._ui.list.viewport().mapToGlobal(pos))
        current_item = self._ui.list.currentItem()

        text = current_item.text()
        index = text.find(' ')
        if index == -1:
            return

        address = QBluetoothAddress(text[0:index])
        if chosen_action == pair_action:
            self._local_device.requestPairing(address, QBluetoothLocalDevice.Paired)
        elif chosen_action == remove_pair_action:
            self._local_device.requestPairing(address, QBluetoothLocalDevice.Unpaired)

    @Slot(QBluetoothAddress, "QBluetoothLocalDevice::Pairing")
    def pairing_done(self, address, pairing):
        items = self._ui.list.findItems(address.toString(), Qt.MatchContains)

        color = QColor(Qt.red)
        if pairing == QBluetoothLocalDevice.Paired or pairing == QBluetoothLocalDevice.AuthorizedPaired:
            color = QColor(Qt.green)
        for item in items:
            item.setForeground(color)
