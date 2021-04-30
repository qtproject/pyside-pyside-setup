
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
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

"""PySide6 port of the network/fortuneserver example from Qt v5.x"""

import random
import sys

from PySide6.QtCore import QByteArray, QDataStream, QIODevice, Qt
from PySide6.QtNetwork import QTcpServer
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout,
                               QLabel, QMessageBox, QPushButton,
                               QVBoxLayout, QWidget)


class Server(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        status_label = QLabel()
        status_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        quit_button = QPushButton("Quit")
        quit_button.setAutoDefault(False)

        self._tcp_server = QTcpServer(self)
        if not self._tcp_server.listen():
            reason = self._tcp_server.errorString()
            QMessageBox.critical(self, "Fortune Server",
                    f"Unable to start the server: {reason}.")
            self.close()
            return
        port = self._tcp_server.serverPort()
        status_label.setText(f"The server is running on port {port}.\nRun the "
                "Fortune Client example now.")

        self.fortunes = (
                "You've been leading a dog's life. Stay off the furniture.",
                "You've got to think about tomorrow.",
                "You will be surprised by a loud noise.",
                "You will feel hungry again in another hour.",
                "You might have mail.",
                "You cannot kill time without injuring eternity.",
                "Computers are not intelligent. They only think they are.")

        quit_button.clicked.connect(self.close)
        self._tcp_server.newConnection.connect(self.send_fortune)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(quit_button)
        button_layout.addStretch(1)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(status_label)
        main_layout.addLayout(button_layout)

        self.setWindowTitle("Fortune Server")

    def send_fortune(self):
        block = QByteArray()
        out = QDataStream(block, QIODevice.WriteOnly)
        out.setVersion(QDataStream.Qt_4_0)
        out.writeUInt16(0)
        fortune = self.fortunes[random.randint(0, len(self.fortunes) - 1)]

        out.writeString(fortune)
        out.device().seek(0)
        out.writeUInt16(block.size() - 2)

        client_connection = self._tcp_server.nextPendingConnection()
        client_connection.disconnected.connect(client_connection.deleteLater)

        client_connection.write(block)
        client_connection.disconnectFromHost()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = Server()
    random.seed(None)
    sys.exit(server.exec())
