# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the network/threadedfortuneserver example from Qt v5.x, originating from PyQt"""

import random

from PySide6.QtCore import (Signal, QByteArray, QDataStream, QIODevice,
        QThread, Qt)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
        QMessageBox, QPushButton, QVBoxLayout)
from PySide6.QtNetwork import (QHostAddress, QNetworkInterface, QTcpServer,
        QTcpSocket)


class FortuneThread(QThread):
    error = Signal(QTcpSocket.SocketError)

    def __init__(self, socketDescriptor, fortune, parent):
        super().__init__(parent)

        self._socket_descriptor = socketDescriptor
        self.text = fortune

    def run(self):
        tcp_socket = QTcpSocket()
        if not tcp_socket.setSocketDescriptor(self._socket_descriptor):
            self.error.emit(tcp_socket.error())
            return

        block = QByteArray()
        outstr = QDataStream(block, QIODevice.WriteOnly)
        outstr.setVersion(QDataStream.Qt_4_0)
        outstr.writeUInt16(0)
        outstr.writeQString(self.text)
        outstr.device().seek(0)
        outstr.writeUInt16(block.size() - 2)

        tcp_socket.write(block)
        tcp_socket.disconnectFromHost()
        tcp_socket.waitForDisconnected()


class FortuneServer(QTcpServer):
    fortunes = (
        "You've been leading a dog's life. Stay off the furniture.",
        "You've got to think about tomorrow.",
        "You will be surprised by a loud noise.",
        "You will feel hungry again in another hour.",
        "You might have mail.",
        "You cannot kill time without injuring eternity.",
        "Computers are not intelligent. They only think they are.")

    def incomingConnection(self, socketDescriptor):
        fortune = self.fortunes[random.randint(0, len(self.fortunes) - 1)]

        thread = FortuneThread(socketDescriptor, fortune, self)
        thread.finished.connect(thread.deleteLater)
        thread.start()


class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.server = FortuneServer()

        status_label = QLabel()
        status_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        status_label.setWordWrap(True)
        quit_button = QPushButton("Quit")
        quit_button.setAutoDefault(False)

        if not self.server.listen():
            reason = self.server.errorString()
            QMessageBox.critical(self, "Threaded Fortune Server",
                    f"Unable to start the server: {reason}.")
            self.close()
            return

        for ip_address in QNetworkInterface.allAddresses():
            if ip_address != QHostAddress.LocalHost and ip_address.toIPv4Address() != 0:
                break
        else:
            ip_address = QHostAddress(QHostAddress.LocalHost)

        ip_address = ip_address.toString()
        port = self.server.serverPort()

        status_label.setText(f"The server is running on\n\nIP: {ip_address}\nport: {port}\n\n"
                "Run the Fortune Client example now.")

        quit_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(quit_button)
        button_layout.addStretch(1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(status_label)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setWindowTitle("Threaded Fortune Server")


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(dialog.exec())
