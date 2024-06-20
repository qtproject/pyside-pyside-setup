# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations
import warnings
from PySide6.QtBluetooth import (QBluetoothDeviceDiscoveryAgent, QLowEnergyController,
                                 QBluetoothDeviceInfo, QBluetoothUuid, QLowEnergyService)
from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QMetaObject, Qt
from PySide6.QtQml import QmlElement, QmlSingleton

from deviceinfo import DeviceInfo
from serviceinfo import ServiceInfo
from characteristicinfo import CharacteristicInfo

QML_IMPORT_NAME = "Scanner"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class Device(QObject):

    devices_updated = Signal()
    services_updated = Signal()
    characteristic_updated = Signal()
    update_changed = Signal()
    state_changed = Signal()
    disconnected = Signal()
    random_address_changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.devices = []
        self._services = []
        self._characteristics = []
        self._previousAddress = ""
        self._message = ""
        self.currentDevice = DeviceInfo()
        self.connected = False
        self.controller: QLowEnergyController = None
        self._deviceScanState = False
        self.random_address = False
        self.discovery_agent = QBluetoothDeviceDiscoveryAgent()
        self.discovery_agent.setLowEnergyDiscoveryTimeout(25000)
        self.discovery_agent.deviceDiscovered.connect(self.add_device)
        self.discovery_agent.errorOccurred.connect(self.device_scan_error)
        self.discovery_agent.finished.connect(self.device_scan_finished)
        self.update = "Search"

    @Property("QVariant", notify=devices_updated)
    def devices_list(self):
        return self.devices

    @Property("QVariant", notify=services_updated)
    def services_list(self):
        return self._services

    @Property("QVariant", notify=characteristic_updated)
    def characteristic_list(self):
        return self._characteristics

    @Property(str, notify=update_changed)
    def update(self):
        return self._message

    @update.setter
    def update(self, message):
        self._message = message
        self.update_changed.emit()

    @Property(bool, notify=random_address_changed)
    def use_random_address(self):
        return self.random_address

    @use_random_address.setter
    def use_random_address(self, newValue):
        self.random_address = newValue
        self.random_address_changed.emit()

    @Property(bool, notify=state_changed)
    def state(self):
        return self._deviceScanState

    @Property(bool)
    def controller_error(self):
        return self.controller and (self.controller.error() != QLowEnergyController.NoError)

    @Slot()
    def start_device_discovery(self):
        self.devices.clear()
        self.devices_updated.emit()
        self.update = "Scanning for devices ..."
        self.discovery_agent.start(QBluetoothDeviceDiscoveryAgent.LowEnergyMethod)

        if self.discovery_agent.isActive():
            self._deviceScanState = True
            self.state_changed.emit()

    @Slot(str)
    def scan_services(self, address):
        # We need the current device for service discovery.
        for device in self.devices:
            if device.device_address == address:
                self.currentDevice.set_device(device.get_device())
                break

        if not self.currentDevice.get_device().isValid():
            warnings.warn("Not a valid device")
            return

        self._characteristics.clear()
        self.characteristic_updated.emit()
        self._services.clear()
        self.services_updated.emit()

        self.update = "Back\n(Connecting to device...)"

        if self.controller and (self._previousAddress != self.currentDevice.device_address):
            self.controller.disconnectFromDevice()
            del self.controller
            self.controller = None

        if not self.controller:
            self.controller = QLowEnergyController.createCentral(self.currentDevice.get_device())
            self.controller.connected.connect(self.device_connected)
            self.controller.errorOccurred.connect(self.error_received)
            self.controller.disconnected.connect(self.device_disconnected)
            self.controller.serviceDiscovered.connect(self.add_low_energy_service)
            self.controller.discoveryFinished.connect(self.services_scan_done)

        if self.random_address:
            self.controller.setRemoteAddressType(QLowEnergyController.RandomAddress)
        else:
            self.controller.setRemoteAddressType(QLowEnergyController.PublicAddress)
        self.controller.connectToDevice()

        self._previousAddress = self.currentDevice.device_address

    @Slot(str)
    def connect_to_service(self, uuid):
        service: QLowEnergyService = None
        for serviceInfo in self._services:
            if not serviceInfo:
                continue

            if serviceInfo.service_uuid == uuid:
                service = serviceInfo.service
                break

        if not service:
            return

        self._characteristics.clear()
        self.characteristic_updated.emit()

        if service.state() == QLowEnergyService.RemoteService:
            service.state_changed.connect(self.service_details_discovered)
            service.discoverDetails()
            self.update = "Back\n(Discovering details...)"
            return

        # discovery already done
        chars = service.characteristics()
        for ch in chars:
            cInfo = CharacteristicInfo(ch)
            self._characteristics.append(cInfo)

        QTimer.singleShot(0, self.characteristic_updated)

    @Slot()
    def disconnect_from_device(self):
        # UI always expects disconnect() signal when calling this signal
        # TODO what is really needed is to extend state() to a multi value
        # and thus allowing UI to keep track of controller progress in addition to
        # device scan progress

        if self.controller.state() != QLowEnergyController.UnconnectedState:
            self.controller.disconnectFromDevice()
        else:
            self.device_disconnected()

    @Slot(QBluetoothDeviceInfo)
    def add_device(self, info):
        if info.coreConfigurations() & QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            self.update = "Last device added: " + info.name()

    @Slot()
    def device_scan_finished(self):
        foundDevices = self.discovery_agent.discoveredDevices()
        for nextDevice in foundDevices:
            if nextDevice.coreConfigurations() & QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
                device = DeviceInfo(nextDevice)
                self.devices.append(device)

        self.devices_updated.emit()
        self._deviceScanState = False
        self.state_changed.emit()
        if not self.devices:
            self.update = "No Low Energy devices found..."
        else:
            self.update = "Done! Scan Again!"

    @Slot("QBluetoothDeviceDiscovertAgent::Error")
    def device_scan_error(self, error):
        if error == QBluetoothDeviceDiscoveryAgent.PoweredOffError:
            self.update = (
                "The Bluetooth adaptor is powered off, power it on before doing discovery."
            )
        elif error == QBluetoothDeviceDiscoveryAgent.InputOutputError:
            self.update = "Writing or reading from the device resulted in an error."
        else:
            qme = self.discovery_agent.metaObject().enumerator(
                self.discovery_agent.metaObject().indexOfEnumerator("Error")
            )
            self.update = f"Error: {qme.valueToKey(error)}"

        self._deviceScanState = False
        self.devices_updated.emit()
        self.state_changed.emit()

    @Slot(QBluetoothUuid)
    def add_low_energy_service(self, service_uuid):
        service = self.controller.createServiceObject(service_uuid)
        if not service:
            warnings.warn("Cannot create service from uuid")
            return

        serv = ServiceInfo(service)
        self._services.append(serv)
        self.services_updated.emit()

    @Slot()
    def device_connected(self):
        self.update = "Back\n(Discovering services...)"
        self.connected = True
        self.controller.discoverServices()

    @Slot("QLowEnergyController::Error")
    def error_received(self, error):
        warnings.warn(f"Error: {self.controller.errorString()}")
        self.update = f"Back\n({self.controller.errorString()})"

    @Slot()
    def services_scan_done(self):
        self.update = "Back\n(Service scan done!)"
        # force UI in case we didn't find anything
        if not self._services:
            self.services_updated.emit()

    @Slot()
    def device_disconnected(self):
        warnings.warn("Disconnect from Device")
        self.disconnected.emit()

    @Slot("QLowEnergyService::ServiceState")
    def service_details_discovered(self, newState):
        if newState != QLowEnergyService.RemoteServiceDiscovered:
            # do not hang in "Scanning for characteristics" mode forever
            # in case the service discovery failed
            # We have to queue the signal up to give UI time to even enter
            # the above mode
            if newState != QLowEnergyService.RemoteServiceDiscovering:
                QMetaObject.invokeMethod(self.characteristic_updated, Qt.QueuedConnection)
            return

        service = self.sender()
        if not service:
            return

        chars = service.characteristics()
        for ch in chars:
            cInfo = CharacteristicInfo(ch)
            self._characteristics.append(cInfo)

        self.characteristic_updated.emit()

    @Slot()
    def stop_device_discovery(self):
        if self.discovery_agent.isActive():
            self.discovery_agent.stop()
