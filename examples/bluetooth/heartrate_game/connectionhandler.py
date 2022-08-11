#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
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

import sys

from PySide6.QtBluetooth import QBluetoothLocalDevice
from PySide6.QtQml import QmlElement
from PySide6.QtCore import QObject, Property, Signal, Slot

from heartrate_global import simulator

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "Shared"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class ConnectionHandler(QObject):

    deviceChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_localDevice = QBluetoothLocalDevice()
        self.m_localDevice.hostModeStateChanged.connect(self.hostModeChanged)

    @Property(bool, notify=deviceChanged)
    def alive(self):
        if sys.platform == "darwin":
            return True
        if simulator:
            return True
        return (self.m_localDevice.isValid()
                and self.m_localDevice.hostMode() != QBluetoothLocalDevice.HostPoweredOff)

    @Property(bool, constant=True)
    def requiresAddressType(self):
        return sys.platform == "linux"  # QT_CONFIG(bluez)?

    @Property(str, notify=deviceChanged)
    def name(self):
        return self.m_localDevice.name()

    @Property(str, notify=deviceChanged)
    def address(self):
        return self.m_localDevice.address().toString()

    @Slot(QBluetoothLocalDevice.HostMode)
    def hostModeChanged(self, mode):
        self.deviceChanged.emit()
