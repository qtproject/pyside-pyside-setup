# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from enum import Enum, auto

from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import (QCapturableWindow, QMediaCaptureSession,
                                  QScreenCapture, QWindowCapture)
from PySide6.QtWidgets import (QGridLayout, QLabel, QListView,
                               QMessageBox, QPushButton, QWidget)
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtCore import QItemSelection, Qt, Slot

from screenlistmodel import ScreenListModel
from windowlistmodel import WindowListModel


class SourceType(Enum):
    Screen = auto()
    Window = auto()


class ScreenCapturePreview(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._source = SourceType.Screen

        self._screen_capture = QScreenCapture(self)
        self._media_capture_session = QMediaCaptureSession(self)
        self._video_widget = QVideoWidget(self)
        self._screen_list_view = QListView(self)
        self._screen_label = QLabel("Select screen to capture:", self)
        self._video_widget_label = QLabel("Capture output:", self)
        self._start_stop_button = QPushButton(self)
        self._status_label = QLabel(self)

        self._screen_list_model = ScreenListModel(self)

        # Setup QScreenCapture with initial source:
        self.setScreen(QGuiApplication.primaryScreen())
        self._screen_capture.start()
        self._media_capture_session.setScreenCapture(self._screen_capture)
        self._media_capture_session.setVideoOutput(self._video_widget)

        self._screen_list_view.setModel(self._screen_list_model)

        self._window_list_view = QListView(self)
        self._window_capture = QWindowCapture(self)
        self._media_capture_session.setWindowCapture(self._window_capture)
        self._window_label = QLabel("Select window to capture:", self)

        self._window_list_model = WindowListModel(self)
        self._window_list_view.setModel(self._window_list_model)
        update_action = QAction("Update windows List", self)
        update_action.triggered.connect(self._window_list_model.populate)
        self._window_list_view.addAction(update_action)
        self._window_list_view.setContextMenuPolicy(Qt.ActionsContextMenu)

        grid_layout = QGridLayout(self)
        grid_layout.addWidget(self._screen_label, 0, 0)
        grid_layout.addWidget(self._screen_list_view, 1, 0)
        grid_layout.addWidget(self._start_stop_button, 4, 0)
        grid_layout.addWidget(self._video_widget_label, 0, 1)
        grid_layout.addWidget(self._video_widget, 1, 1, 4, 1)
        grid_layout.addWidget(self._window_label, 2, 0)
        grid_layout.addWidget(self._window_list_view, 3, 0)
        grid_layout.addWidget(self._status_label, 5, 0, 1, 2)

        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnMinimumWidth(0, 400)
        grid_layout.setColumnMinimumWidth(1, 400)
        grid_layout.setRowMinimumHeight(3, 1)

        selection_model = self._screen_list_view.selectionModel()
        selection_model.selectionChanged.connect(self.on_current_screen_selection_changed)
        selection_model = self._window_list_view.selectionModel()
        selection_model.selectionChanged.connect(self.on_current_window_selection_changed)

        self._start_stop_button.clicked.connect(self.on_start_stop_button_clicked)
        self._screen_capture.errorOccurred.connect(self.on_screen_capture_error_occured,
                                                   Qt.QueuedConnection)
        self._window_capture.errorOccurred.connect(self.on_window_capture_error_occured,
                                                   Qt.QueuedConnection)
        self.update_active(SourceType.Screen, True)

    @Slot(QItemSelection)
    def on_current_screen_selection_changed(self, selection):
        self.clear_error_string()
        indexes = selection.indexes()
        if indexes:
            self._screen_capture.setScreen(self._screen_list_model.screen(indexes[0]))
            self.update_active(SourceType.Screen, self.is_active())
            self._window_list_view.clearSelection()
        else:
            self._screen_capture.setScreen(None)

    @Slot(QItemSelection)
    def on_current_window_selection_changed(self, selection):
        self.clear_error_string()
        indexes = selection.indexes()
        if indexes:
            window = self._window_list_model.window(indexes[0])
            if not window.isValid():
                m = "The window is no longer valid. Update the list of windows?"
                answer = QMessageBox.question(self, "Invalid window", m)
                if answer == QMessageBox.Yes:
                    self.update_active(SourceType.Window, False)
                    self._window_list_view.clearSelection()
                    self._window_list_model.populate()
                    return
            self._window_capture.setWindow(window)
            self.update_active(SourceType.Window, self.is_active())
            self._screen_list_view.clearSelection()
        else:
            self._window_capture.setWindow(QCapturableWindow())

    @Slot(QWindowCapture.Error, str)
    def on_window_capture_error_occured(self, error, error_string):
        self.set_error_string("QWindowCapture: Error occurred " + error_string)

    @Slot(QScreenCapture.Error, str)
    def on_screen_capture_error_occured(self, error, error_string):
        self.set_error_string("QScreenCapture: Error occurred " + error_string)

    def set_error_string(self, t):
        self._status_label.setStyleSheet("background-color: rgb(255, 0, 0);")
        self._status_label.setText(t)

    def clear_error_string(self):
        self._status_label.clear()
        self._status_label.setStyleSheet("")

    @Slot()
    def on_start_stop_button_clicked(self):
        self.clear_error_string()
        self.update_active(self._source_type, not self.is_active())

    def update_start_stop_button_text(self):
        active = self.is_active()
        if self._source_type == SourceType.Window:
            m = "Stop window capture" if active else "Start window capture"
            self._start_stop_button.setText(m)
        elif self._source_type == SourceType.Screen:
            m = "Stop screen capture" if active else "Start screen capture"
            self._start_stop_button.setText(m)

    def update_active(self, source_type, active):
        self._source_type = source_type
        self._screen_capture.setActive(active and source_type == SourceType.Screen)
        self._window_capture.setActive(active and source_type == SourceType.Window)

        self.update_start_stop_button_text()

    def is_active(self):
        if self._source_type == SourceType.Window:
            return self._window_capture.isActive()
        if self._source_type == SourceType.Screen:
            return self._screen_capture.isActive()
        return False
