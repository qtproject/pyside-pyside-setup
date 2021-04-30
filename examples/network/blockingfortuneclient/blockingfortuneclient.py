
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2016 The Qt Company Ltd.
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

"""PySide6 port of the network/blockingfortunclient example from Qt v5.x, originating from PyQt"""

from PySide6.QtCore import (Signal, QDataStream, QMutex, QMutexLocker,
        QThread, QWaitCondition)
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (QApplication, QDialogButtonBox, QGridLayout,
        QLabel, QLineEdit, QMessageBox, QPushButton, QWidget)
from PySide6.QtNetwork import (QAbstractSocket, QHostAddress, QNetworkInterface,
        QTcpSocket)


class FortuneThread(QThread):
    new_fortune = Signal(str)

    error = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.quit = False
        self._host_name = ''
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.port = 0

    def __del__(self):
        self.mutex.lock()
        self.quit = True
        self.cond.wakeOne()
        self.mutex.unlock()
        self.wait()

    def request_new_fortune(self, hostname, port):
        locker = QMutexLocker(self.mutex)
        self._host_name = hostname
        self.port = port
        if not self.isRunning():
            self.start()
        else:
            self.cond.wakeOne()

    def run(self):
        self.mutex.lock()
        server_name = self._host_name
        server_port = self.port
        self.mutex.unlock()

        while not self.quit:
            timeout = 5 * 1000

            socket = QTcpSocket()
            socket.connectToHost(server_name, server_port)

            if not socket.waitForConnected(timeout):
                self.error.emit(socket.error(), socket.errorString())
                return

            while socket.bytesAvailable() < 2:
                if not socket.waitForReadyRead(timeout):
                    self.error.emit(socket.error(), socket.errorString())
                    return

            instr = QDataStream(socket)
            instr.setVersion(QDataStream.Qt_4_0)
            block_size = instr.readUInt16()

            while socket.bytesAvailable() < block_size:
                if not socket.waitForReadyRead(timeout):
                    self.error.emit(socket.error(), socket.errorString())
                    return

            self.mutex.lock()
            fortune = instr.readQString()
            self.new_fortune.emit(fortune)

            self.cond.wait(self.mutex)
            server_name = self._host_name
            server_port = self.port
            self.mutex.unlock()


class BlockingClient(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.thread = FortuneThread()
        self._current_fortune = ''

        host_label = QLabel("&Server name:")
        port_label = QLabel("S&erver port:")

        for ip_address in QNetworkInterface.allAddresses():
            if ip_address != QHostAddress.LocalHost and ip_address.toIPv4Address() != 0:
                break
        else:
            ip_address = QHostAddress(QHostAddress.LocalHost)

        ip_address = ip_address.toString()

        self._host_line_edit = QLineEdit(ip_address)
        self._port_line_edit = QLineEdit()
        self._port_line_edit.setValidator(QIntValidator(1, 65535, self))

        host_label.setBuddy(self._host_line_edit)
        port_label.setBuddy(self._port_line_edit)

        self._status_label = QLabel(
                "This example requires that you run the Fortune Server example as well.")
        self._status_label.setWordWrap(True)

        self._get_fortune_button = QPushButton("Get Fortune")
        self._get_fortune_button.setDefault(True)
        self._get_fortune_button.setEnabled(False)

        quit_button = QPushButton("Quit")

        button_box = QDialogButtonBox()
        button_box.addButton(self._get_fortune_button, QDialogButtonBox.ActionRole)
        button_box.addButton(quit_button, QDialogButtonBox.RejectRole)

        self._get_fortune_button.clicked.connect(self.request_new_fortune)
        quit_button.clicked.connect(self.close)
        self._host_line_edit.textChanged.connect(self.enable_get_fortune_button)
        self._port_line_edit.textChanged.connect(self.enable_get_fortune_button)
        self.thread.new_fortune.connect(self.show_fortune)
        self.thread.error.connect(self.display_error)

        main_layout = QGridLayout()
        main_layout.addWidget(host_label, 0, 0)
        main_layout.addWidget(self._host_line_edit, 0, 1)
        main_layout.addWidget(port_label, 1, 0)
        main_layout.addWidget(self._port_line_edit, 1, 1)
        main_layout.addWidget(self._status_label, 2, 0, 1, 2)
        main_layout.addWidget(button_box, 3, 0, 1, 2)
        self.setLayout(main_layout)

        self.setWindowTitle("Blocking Fortune Client")
        self._port_line_edit.setFocus()

    def request_new_fortune(self):
        self._get_fortune_button.setEnabled(False)
        self.thread.request_new_fortune(self._host_line_edit.text(),
                int(self._port_line_edit.text()))

    def show_fortune(self, nextFortune):
        if nextFortune == self._current_fortune:
            self.request_new_fortune()
            return

        self._current_fortune = nextFortune
        self._status_label.setText(self._current_fortune)
        self._get_fortune_button.setEnabled(True)

    def display_error(self, socketError, message):
        if socketError == QAbstractSocket.HostNotFoundError:
            QMessageBox.information(self, "Blocking Fortune Client",
                    "The host was not found. Please check the host and port "
                    "settings.")
        elif socketError == QAbstractSocket.ConnectionRefusedError:
            QMessageBox.information(self, "Blocking Fortune Client",
                    "The connection was refused by the peer. Make sure the "
                    "fortune server is running, and check that the host name "
                    "and port settings are correct.")
        else:
            QMessageBox.information(self, "Blocking Fortune Client",
                    f"The following error occurred: {message}.")

        self._get_fortune_button.setEnabled(True)

    def enable_get_fortune_button(self):
        self._get_fortune_button.setEnabled(self._host_line_edit.text() != '' and
                self._port_line_edit.text() != '')


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    client = BlockingClient()
    client.show()
    sys.exit(app.exec())
