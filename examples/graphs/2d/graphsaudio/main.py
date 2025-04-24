# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from pathlib import Path
from PySide6.QtCore import QObject, QPointF, Slot, Signal
from PySide6.QtMultimedia import QAudioFormat, QAudioSource, QMediaDevices
from PySide6.QtWidgets import QMessageBox
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication


SAMPLE_COUNT = 2000
RESOLUTION = 4


class Audio(QObject):
    dataUpdated = Signal(list)

    def __init__(self, device):
        super().__init__()

        format_audio = QAudioFormat()
        format_audio.setSampleRate(8000)
        format_audio.setChannelCount(1)
        format_audio.setSampleFormat(QAudioFormat.UInt8)

        self.device_name = device.description()

        self._audio_input = QAudioSource(device, format_audio, self)
        self._io_device = self._audio_input.start()
        self._io_device.readyRead.connect(self._readyRead)

        self._buffer = [QPointF(x, 0) for x in range(SAMPLE_COUNT)]

    def closeEvent(self, event):
        if self._audio_input is not None:
            self._audio_input.stop()
        event.accept()

    @Slot()
    def _readyRead(self):
        data = self._io_device.readAll()
        available_samples = data.size() // RESOLUTION
        start = 0
        if (available_samples < SAMPLE_COUNT):
            start = SAMPLE_COUNT - available_samples
            for s in range(start):
                self._buffer[s].setY(self._buffer[s + available_samples].y())

        data_index = 0
        for s in range(start, SAMPLE_COUNT):
            value = (ord(data[data_index]) - 128) / 128
            self._buffer[s].setY(value)
            data_index = data_index + RESOLUTION

        self.dataUpdated.emit(self._buffer)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    input_devices = QMediaDevices.audioInputs()
    if not input_devices:
        QMessageBox.warning(None, "audio", "There is no audio input device available.")
        sys.exit(-1)

    audio_bridge = Audio(input_devices[0])
    engine.rootContext().setContextProperty("audio_bridge", audio_bridge)

    device = input_devices[0]
    device_name = device.description()
    engine.rootContext().setContextProperty("device_name", device_name)

    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("GraphsAudio", "Main")

    sys.exit(app.exec())
