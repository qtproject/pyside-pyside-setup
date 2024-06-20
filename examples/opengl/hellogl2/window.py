# Copyright (C) 2023 The Qt Company Ltd.
# Copyright (C) 2013 Riverbank Computing Limited.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QHBoxLayout, QMainWindow,
                               QMessageBox, QPushButton, QSlider,
                               QVBoxLayout, QWidget)

from glwidget import GLWidget


def _main_window():
    for t in qApp.topLevelWidgets():  # noqa: F821
        if isinstance(t, QMainWindow):
            return t
    return None


class Window(QWidget):
    instances = []  # Keep references when undocked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.instances.append(self)

        self._gl_widget = GLWidget()

        self._x_slider = self.create_slider()
        self._x_slider.valueChanged.connect(self._gl_widget.set_xrotation)
        self._gl_widget.x_rotation_changed.connect(self._x_slider.setValue)

        self._y_slider = self.create_slider()
        self._y_slider.valueChanged.connect(self._gl_widget.set_yrotation)
        self._gl_widget.y_rotation_changed.connect(self._y_slider.setValue)

        self._z_slider = self.create_slider()
        self._z_slider.valueChanged.connect(self._gl_widget.set_zrotation)
        self._gl_widget.z_rotation_changed.connect(self._z_slider.setValue)

        mainLayout = QVBoxLayout(self)
        w = QWidget()
        container = QHBoxLayout(w)
        container.addWidget(self._gl_widget)
        container.addWidget(self._x_slider)
        container.addWidget(self._y_slider)
        container.addWidget(self._z_slider)

        mainLayout.addWidget(w)
        self._dock_btn = QPushButton("Undock")
        self._dock_btn.clicked.connect(self.dock_undock)
        mainLayout.addWidget(self._dock_btn)

        self._x_slider.setValue(15 * 16)
        self._y_slider.setValue(345 * 16)
        self._z_slider.setValue(0 * 16)

        self.setWindowTitle(self.tr("Hello GL"))

    def create_slider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)
        return slider

    def closeEvent(self, event):
        self.instances.remove(self)
        event.accept()

    def keyPressEvent(self, event):
        if self.isWindow() and event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    @Slot()
    def dock_undock(self):
        if self.parent():
            self.undock()
        else:
            self.dock()

    def dock(self):
        mainWindow = _main_window()
        if not mainWindow or not mainWindow.isVisible():
            QMessageBox.information(self, "Cannot Dock",
                                    "Main window already closed")
            return
        if mainWindow.centralWidget():
            QMessageBox.information(self, "Cannot Dock",
                                    "Main window already occupied")
            return

        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self._dock_btn.setText("Undock")
        mainWindow.setCentralWidget(self)

    def undock(self):
        self.setParent(None)
        self.setAttribute(Qt.WA_DeleteOnClose)
        geometry = self.screen().availableGeometry()
        x = geometry.x() + (geometry.width() - self.width()) / 2
        y = geometry.y() + (geometry.height() - self.height()) / 2
        self.move(x, y)
        self._dock_btn.setText("Dock")
        self.show()
