#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtBluetooth import (QBluetoothAddress, QBluetoothServiceInfo,
                                 QBluetoothServiceDiscoveryAgent, QBluetoothLocalDevice)

from ui_service import Ui_ServiceDiscovery


class ServiceDiscoveryDialog(QDialog):
    def __init__(self, name, address, parent=None):
        super().__init__(parent)
        self._ui = Ui_ServiceDiscovery()
        self._ui.setupUi(self)

        # Using default Bluetooth adapter
        local_device = QBluetoothLocalDevice()
        adapter_address = QBluetoothAddress(local_device.address())

        # In case of multiple Bluetooth adapters it is possible to
        # set which adapter will be used by providing MAC Address.
        # Example code:
        #
        # adapterAddress = QBluetoothAddress("XX:XX:XX:XX:XX:XX")
        # discoveryAgent = QBluetoothServiceDiscoveryAgent(adapterAddress)

        self._discovery_agent = QBluetoothServiceDiscoveryAgent(adapter_address)
        self._discovery_agent.setRemoteAddress(address)

        self.setWindowTitle(name)

        self._discovery_agent.serviceDiscovered.connect(self.add_service)
        self._discovery_agent.finished.connect(self._ui.status.hide)
        self._discovery_agent.start()

    @Slot(QBluetoothServiceInfo)
    def add_service(self, info):
        line = info.serviceName()
        if not line:
            return

        if info.serviceDescription():
            line += "\n\t" + info.serviceDescription()
        if info.serviceProvider():
            line += "\n\t" + info.serviceProvider()
        self._ui.list.addItem(line)
