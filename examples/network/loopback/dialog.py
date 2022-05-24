# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import (QAbstractSocket, QHostAddress, QTcpServer,
                               QTcpSocket)
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QMessageBox,
                               QProgressBar, QPushButton, QVBoxLayout)


class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.total_bytes = 50 * 1024 * 1024  # 50 MB
        self.payload_size = 64 * 1024  # 64 KB

        self.bytes_to_write = 0
        self.bytes_written = 0
        self.bytes_received = 0

        self.client_progress_bar = QProgressBar()
        self.client_status_label = QLabel("Client ready")
        self.server_progress_bar = QProgressBar()
        self.server_status_label = QLabel("Server ready")

        self.start_button = QPushButton("&Start")
        self.quit_button = QPushButton("&Quit")

        self.button_box = QDialogButtonBox()
        self.button_box.addButton(self.start_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.quit_button, QDialogButtonBox.RejectRole)

        self.start_button.clicked.connect(self.start)
        self.quit_button.clicked.connect(self.close)

        self.tcp_server = QTcpServer()
        self.tcp_client = QTcpSocket()
        self.tcp_server.newConnection.connect(self.accept_connection)
        self.tcp_client.connected.connect(self.start_transfer)
        self.tcp_client.bytesWritten.connect(self.update_client_progress)
        self.tcp_client.errorOccurred.connect(self.display_error)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.client_progress_bar)
        main_layout.addWidget(self.client_status_label)
        main_layout.addWidget(self.server_progress_bar)
        main_layout.addWidget(self.server_status_label)
        main_layout.addStretch(1)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        self.setWindowTitle("Loopback")

    def start(self):

        self.start_button.setEnabled(False)

        QGuiApplication.setOverrideCursor(Qt.WaitCursor)

        self.bytes_written = 0
        self.bytes_received = 0

        while not self.tcp_server.isListening() and not self.tcp_server.listen():
            ret: QMessageBox.StandardButton = QMessageBox.critical(
                self,
                "Loopback",
                f"Unable to start the test {self.tcp_server.errorString()}",
                QMessageBox.Retry | QMessageBox.Cancel,
            )
            if ret == QMessageBox.Cancel:
                return

        self.server_status_label.setText("Listening")
        self.client_status_label.setText("Connecting")
        self.tcp_client.connectToHost(QHostAddress.LocalHost, self.tcp_server.serverPort())

    def accept_connection(self):

        self.tcp_server_connection = self.tcp_server.nextPendingConnection()
        if not self.tcp_server_connection:
            self.server_status_label.setText("Error: got invalid pending connection")
            return

        self.tcp_server_connection.readyRead.connect(self.update_server_progress)
        self.tcp_server_connection.errorOccurred.connect(self.display_error)
        self.tcp_server_connection.disconnected.connect(self.tcp_server_connection.deleteLater)

        self.server_status_label.setText("Accepted connection")
        self.tcp_server.close()

    def start_transfer(self):

        # Called when the TCP client has connected to the loopback server
        self.bytes_to_write = self.total_bytes - self.tcp_client.write(
            QByteArray(self.payload_size, "@")
        )
        self.client_status_label.setText("Connected")

    def update_server_progress(self):

        self.bytes_received += self.tcp_server_connection.bytesAvailable()
        self.tcp_server_connection.readAll()

        self.server_progress_bar.setMaximum(self.total_bytes)
        self.server_progress_bar.setValue(self.bytes_received)
        self.server_status_label.setText(f"Received {self.bytes_received / (1024 ** 2)} MB")

        if self.bytes_received == self.total_bytes:

            self.tcp_server_connection.close()
            self.start_button.setEnabled(True)

            QGuiApplication.restoreOverrideCursor()

    def update_client_progress(self, num_bytes: int):

        # called when the TCP client has written some bytes
        self.bytes_written += num_bytes

        # only write more if not finished and when the Qt write buffer is below a certain size
        if self.bytes_to_write > 0 and self.tcp_client.bytesToWrite() <= 4 * self.payload_size:
            self.bytes_to_write -= self.tcp_client.write(
                QByteArray(min(self.bytes_to_write, self.payload_size), "@")
            )

        self.client_progress_bar.setMaximum(self.total_bytes)
        self.client_progress_bar.setValue(self.bytes_written)
        self.client_status_label.setText(f"Sent {self.bytes_written / (1024 ** 2)} MB")

    def display_error(self, socket_error: QAbstractSocket.SocketError):
        if socket_error == QAbstractSocket.RemoteHostClosedError:
            return

        QMessageBox.information(
            self,
            "Network error",
            f"The following error occurred: {self.tcp_client.errorString()}",
        )

        self.tcp_client.close()
        self.tcp_server.close()
        self.client_progress_bar.reset()
        self.server_progress_bar.reset()
        self.client_status_label.setText("Client ready")
        self.server_status_label.setText("Server ready")
        self.start_button.setEnabled(True)

        QGuiApplication.restoreOverrideCursor()
