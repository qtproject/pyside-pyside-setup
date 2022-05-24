# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""
PySide6 port of Qt6 example examples/multimedia/audiosources

Audio Devices demonstrates how to create a simple application to list and test
the configuration for the various audio devices available on the target device
or desktop PC.

Note: This Python example is not fully complete as compared to its C++ counterpart.
Only the push mode works at the moment. For the pull mode to work, the class
QIODevice have python bindings that needs to be fixed.
"""
import sys
from typing import Optional

import PySide6
from PySide6.QtCore import QByteArray, QIODevice, QMargins, QRect, Qt, Signal, Slot
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtMultimedia import (
    QAudio,
    QAudioDevice,
    QAudioFormat,
    QAudioSource,
    QMediaDevices,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class AudioInfo:
    def __init__(self, format: QAudioFormat):
        super().__init__()
        self.m_format = format
        self.m_level = 0.0

    def calculate_level(self, data: bytes, length: int) -> float:
        channel_bytes: int = int(self.m_format.bytesPerSample())
        sample_bytes: int = int(self.m_format.bytesPerFrame())
        num_samples: int = int(length / sample_bytes)

        maxValue: float = 0
        m_offset: int = 0

        for i in range(num_samples):
            for j in range(self.m_format.channelCount()):
                value = 0
                if len(data) > m_offset:
                    data_sample = data[m_offset:]
                    value = self.m_format.normalizedSampleValue(data_sample)
                maxValue = max(value, maxValue)
                m_offset = m_offset + channel_bytes

        return maxValue


class RenderArea(QWidget):
    def __init__(self, parent: Optional[PySide6.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.m_level = 0
        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)
        self.setMinimumHeight(30)
        self.setMinimumWidth(200)

    def set_level(self, value):
        self.m_level = value
        self.update()

    def paintEvent(self, event: PySide6.QtGui.QPaintEvent) -> None:
        with QPainter(self) as painter:
            painter.setPen(Qt.black)
            frame = painter.viewport() - QMargins(10, 10, 10, 10)

            painter.drawRect(frame)

            if self.m_level == 0.0:
                return

            pos: int = round((frame.width() - 1) * self.m_level)
            painter.fillRect(
                frame.left() + 1, frame.top() + 1, pos, frame.height() - 1, Qt.red
            )


class InputTest(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.m_devices = QMediaDevices(self)
        self.m_pullMode = False

        self.initialize_window()
        self.initialize_audio(QMediaDevices.defaultAudioInput())

    def initialize_window(self):
        self.layout = QVBoxLayout(self)

        self.m_canvas = RenderArea(self)
        self.layout.addWidget(self.m_canvas)

        self.m_device_box = QComboBox(self)
        default_device_info = QMediaDevices.defaultAudioInput()
        self.m_device_box.addItem(
            default_device_info.description(), default_device_info
        )

        for device_info in self.m_devices.audioInputs():
            if device_info != default_device_info:
                self.m_device_box.addItem(device_info.description(), device_info)

        self.m_device_box.activated[int].connect(self.device_changed)
        self.layout.addWidget(self.m_device_box)

        self.m_volume_slider = QSlider(Qt.Horizontal, self)
        self.m_volume_slider.setRange(0, 100)
        self.m_volume_slider.setValue(100)
        self.m_volume_slider.valueChanged.connect(self.slider_changed)
        self.layout.addWidget(self.m_volume_slider)

        self.m_mode_button = QPushButton(self)
        self.m_mode_button.clicked.connect(self.toggle_mode)
        self.layout.addWidget(self.m_mode_button)

        self.m_suspend_resume_button = QPushButton(self)
        self.m_suspend_resume_button.clicked.connect(self.toggle_suspend)
        self.layout.addWidget(self.m_suspend_resume_button)

    def initialize_audio(self, device_info: QAudioDevice):
        format = QAudioFormat()
        format.setSampleRate(8000)
        format.setChannelCount(1)
        format.setSampleFormat(QAudioFormat.Int16)

        self.m_audio_info = AudioInfo(format)

        self.m_audio_input = QAudioSource(device_info, format)
        initial_volume = QAudio.convertVolume(
            self.m_audio_input.volume(),
            QAudio.LinearVolumeScale,
            QAudio.LogarithmicVolumeScale,
        )
        self.m_volume_slider.setValue(int(round(initial_volume * 100)))
        self.toggle_mode()

    @Slot()
    def toggle_mode(self):
        self.m_audio_input.stop()
        self.toggle_suspend()

        self.m_mode_button.setText("Enable pull mode")
        io = self.m_audio_input.start()

        def push_mode_slot():
            len = self.m_audio_input.bytesAvailable()
            buffer_size = 4096
            if len > buffer_size:
                len = buffer_size
            buffer: QByteArray = io.read(len)
            if len > 0:
                level = self.m_audio_info.calculate_level(buffer, len)
                self.m_canvas.set_level(level)

        io.readyRead.connect(push_mode_slot)

    @Slot()
    def toggle_suspend(self):
        # toggle suspend/resume
        state = self.m_audio_input.state()
        if (state == QAudio.SuspendedState) or (state == QAudio.StoppedState):
            self.m_audio_input.resume()
            self.m_suspend_resume_button.setText("Suspend recording")
        elif state == QAudio.ActiveState:
            self.m_audio_input.suspend()
            self.m_suspend_resume_button.setText("Resume recording")
        # else no-op

    @Slot(int)
    def device_changed(self, index):
        self.m_audio_input.stop()
        self.m_audio_input.disconnect(self)
        self.initialize_audio(self.m_device_box.itemData(index))

    @Slot(int)
    def slider_changed(self, value):
        linearVolume = QAudio.convertVolume(
            value / float(100), QAudio.LogarithmicVolumeScale, QAudio.LinearVolumeScale
        )

        self.m_audio_input.setVolume(linearVolume)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Sources Example")
    input = InputTest()
    input.show()
    sys.exit(app.exec())
