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

"""PySide6 port of the QtDBus pingpong example from Qt v6.x (ping client)"""

import sys
from PySide6.QtCore import QCoreApplication, QObject, Slot
from PySide6.QtDBus import QDBusConnection,  QDBusInterface, QDBusReply


SERVICE_NAME = 'org.example.QtDBus.PingExample'


if __name__ == "__main__":
    app = QCoreApplication()
    session_bus = QDBusConnection.sessionBus()
    if not session_bus.isConnected():
        print("Cannot connect to the D-Bus session bus.\n"
              "To start it, run:\n"
              "\teval `dbus-launch --auto-syntax`\n")
        sys.exit(-1)

    iface = QDBusInterface(SERVICE_NAME, '/', '', session_bus)
    if not iface.isValid():
        print(session_bus.lastError().message())
        sys.exit(-1)

    argument = sys.argv[1] if len(sys.argv) > 1 else 'Hello'
    message = iface.call('ping', argument)
    reply = QDBusReply(message)
    if not reply.isValid():
        error = reply.error().message()
        print(f'ping: Call failed: {error}')
        sys.exit(-1)

    value = reply.value()
    print(f'ping: Reply was: {value}')
    sys.exit(0)

