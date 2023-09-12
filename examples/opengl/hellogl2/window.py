# Copyright (C) 2023 The Qt Company Ltd.
# Copyright (C) 2013 Riverbank Computing Limited.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QSlider, QWidget)

from glwidget import GLWidget


class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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

        main_layout = QHBoxLayout()
        main_layout.addWidget(self._gl_widget)
        main_layout.addWidget(self._x_slider)
        main_layout.addWidget(self._y_slider)
        main_layout.addWidget(self._z_slider)
        self.setLayout(main_layout)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
