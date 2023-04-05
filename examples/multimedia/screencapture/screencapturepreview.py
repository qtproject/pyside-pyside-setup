# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QScreenCapture, QMediaCaptureSession
from PySide6.QtWidgets import (QGridLayout, QLabel, QListView,
                               QMessageBox, QPushButton, QWidget)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Slot

from screenlistmodel import ScreenListModel


class ScreenCapturePreview(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._screen_capture = QScreenCapture(self)
        self._media_capture_session = QMediaCaptureSession(self)
        self._video_widget = QVideoWidget(self)
        self._screen_list_view = QListView(self)
        self._screen_label = QLabel("Double-click screen to capture:", self)
        self._video_widget_label = QLabel("QScreenCapture output:", self)
        self._start_stop_button = QPushButton("Stop screencapture", self)

        self._screen_list_model = ScreenListModel(self)

        # Setup QScreenCapture with initial source:
        self.set_screen(QGuiApplication.primaryScreen())
        self._screen_capture.start()
        self._media_capture_session.setScreenCapture(self._screen_capture)
        self._media_capture_session.setVideoOutput(self._video_widget)

        self._screen_list_view.setModel(self._screen_list_model)

        grid_layout = QGridLayout(self)
        grid_layout.addWidget(self._screen_label, 0, 0)
        grid_layout.addWidget(self._screen_list_view, 1, 0)
        grid_layout.addWidget(self._start_stop_button, 2, 0)
        grid_layout.addWidget(self._video_widget_label, 0, 1)
        grid_layout.addWidget(self._video_widget, 1, 1, 2, 1)

        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnMinimumWidth(0, 400)
        grid_layout.setColumnMinimumWidth(1, 400)

        self._screen_list_view.activated.connect(self.on_screen_selection_changed)
        self._start_stop_button.clicked.connect(self.on_start_stop_button_clicked)
        self._screen_capture.errorOccurred.connect(self.on_screen_capture_error_occured)

    def set_screen(self, screen):
        self._screen_capture.setScreen(screen)
        self.setWindowTitle(f"Capturing {screen.name()}")

    @Slot()
    def on_screen_selection_changed(self, index):
        self.set_screen(self._screen_list_model.screen(index))

    @Slot()
    def on_screen_capture_error_occured(self, error, errorString):
        QMessageBox.warning(self, "QScreenCapture: Error occurred",
                            errorString)

    @Slot()
    def on_start_stop_button_clicked(self):
        if self._screen_capture.isActive():
            self._screen_capture.stop()
            self._start_stop_button.setText("Start screencapture")
        else:
            self._screen_capture.start()
            self._start_stop_button.setText("Stop screencapture")
