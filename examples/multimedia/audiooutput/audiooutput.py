
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

"""PySide6 port of the multimedia/audiooutput example from Qt v5.x, originating from PyQt"""

import sys
from math import pi, sin
from struct import pack

from PySide6.QtCore import (QByteArray, QIODevice, Qt, QSysInfo, QTimer,
                            qWarning, Slot)
from PySide6.QtMultimedia import (QAudio, QAudioDevice, QAudioFormat,
                                  QAudioSink, QMediaDevices)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QSlider,
                               QVBoxLayout, QWidget)


class Generator(QIODevice):

    def __init__(self, format, durationUs, sampleRate, parent):
        super().__init__(parent)

        self.m_pos = 0
        self.m_buffer = QByteArray()

        self.generate_data(format, durationUs, sampleRate)

    def start(self):
        self.open(QIODevice.ReadOnly)

    def stop(self):
        self.m_pos = 0
        self.close()

    def generate_data(self, fmt, durationUs, sampleRate):
        pack_format = ''

        sample_size = fmt.bytesPerSample() * 8
        if sample_size == 8:
            if fmt.sampleFormat() == QAudioFormat.UInt8:
                scaler = lambda x: ((1.0 + x) / 2 * 255)
                pack_format = 'B'
            elif fmt.sampleFormat() == QAudioFormat.Int16:
                scaler = lambda x: x * 127
                pack_format = 'b'
        elif sample_size == 16:
            little_endian = QSysInfo.ByteOrder == QSysInfo.LittleEndian
            if fmt.sampleFormat() == QAudioFormat.UInt8:
                scaler = lambda x: (1.0 + x) / 2 * 65535
                pack_format = '<H' if little_endian else '>H'
            elif fmt.sampleFormat() == QAudioFormat.Int16:
                scaler = lambda x: x * 32767
                pack_format = '<h' if little_endian else '>h'

        assert(pack_format != '')

        channel_bytes = fmt.bytesPerSample()
        sample_bytes = fmt.channelCount() * channel_bytes

        length = (fmt.sampleRate() * fmt.channelCount() * channel_bytes) * durationUs // 100000

        self.m_buffer.clear()
        sample_index = 0
        factor = 2 * pi * sampleRate / fmt.sampleRate()

        while length != 0:
            x = sin((sample_index % fmt.sampleRate()) * factor)
            packed = pack(pack_format, int(scaler(x)))

            for _ in range(fmt.channelCount()):
                self.m_buffer.append(packed)
                length -= channel_bytes

            sample_index += 1

    def readData(self, maxlen):
        data = QByteArray()
        total = 0

        while maxlen > total:
            chunk = min(self.m_buffer.size() - self.m_pos, maxlen - total)
            data.append(self.m_buffer.mid(self.m_pos, chunk))
            self.m_pos = (self.m_pos + chunk) % self.m_buffer.size()
            total += chunk

        return data.data()

    def writeData(self, data):
        return 0

    def bytesAvailable(self):
        return self.m_buffer.size() + super(Generator, self).bytesAvailable()


class AudioTest(QMainWindow):

    PUSH_MODE_LABEL = "Enable push mode"
    PULL_MODE_LABEL = "Enable pull mode"
    SUSPEND_LABEL = "Suspend playback"
    RESUME_LABEL = "Resume playback"

    DURATION_SECONDS = 1
    TONE_SAMPLE_RATE_HZ = 600
    DATA_SAMPLE_RATE_HZ = 44100

    def __init__(self, devices):
        super().__init__()

        self.m_devices = devices
        self.m_device = self.m_devices[0]
        self.m_output = None

        self.initialize_window()
        self.initialize_audio()

    def initialize_window(self):

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.m_deviceBox = QComboBox()
        self.m_deviceBox.activated[int].connect(self.device_changed)
        for deviceInfo in self.m_devices:
            self.m_deviceBox.addItem(deviceInfo.description(), deviceInfo)

        layout.addWidget(self.m_deviceBox)

        self.m_modeButton = QPushButton()
        self.m_modeButton.clicked.connect(self.toggle_mode)
        self.m_modeButton.setText(self.PUSH_MODE_LABEL)

        layout.addWidget(self.m_modeButton)

        self.m_suspendResumeButton = QPushButton(
                clicked=self.toggle_suspend_resume)
        self.m_suspendResumeButton.setText(self.SUSPEND_LABEL)

        layout.addWidget(self.m_suspendResumeButton)

        volume_box = QHBoxLayout()
        volume_label = QLabel("Volume:")
        self.m_volumeSlider = QSlider(Qt.Horizontal, minimum=0, maximum=100,
                singleStep=10)
        self.m_volumeSlider.valueChanged.connect(self.volume_changed)

        volume_box.addWidget(volume_label)
        volume_box.addWidget(self.m_volumeSlider)

        layout.addLayout(volume_box)

        self.setCentralWidget(central_widget)

    def initialize_audio(self):
        self.m_pullTimer = QTimer(self)
        self.m_pullTimer.timeout.connect(self.pull_timer_expired)
        self.m_pullMode = True

        self.m_format = QAudioFormat()
        self.m_format.setSampleRate(self.DATA_SAMPLE_RATE_HZ)
        self.m_format.setChannelCount(1)
        self.m_format.setSampleFormat(QAudioFormat.Int16)

        info = self.m_devices[0]
        if not info.isFormatSupported(self.m_format):
            qWarning("Default format not supported - trying to use nearest")
            self.m_format = info.nearestFormat(self.m_format)

        self.m_generator = Generator(self.m_format,
                self.DURATION_SECONDS * 1000000, self.TONE_SAMPLE_RATE_HZ, self)

        self.create_audio_output()

    def create_audio_output(self):
        self.m_audioSink = QAudioSink(self.m_device, self.m_format)
        self.m_audioSink.stateChanged.connect(self.handle_state_changed)

        self.m_generator.start()
        self.m_audioSink.start(self.m_generator)
        self.m_volumeSlider.setValue(self.m_audioSink.volume() * 100)

    @Slot(int)
    def device_changed(self, index):
        self.m_pullTimer.stop()
        self.m_generator.stop()
        self.m_audioSink.stop()
        self.m_device = self.m_deviceBox.itemData(index)

        self.create_audio_output()

    @Slot(int)
    def volume_changed(self, value):
        if self.m_audioSink is not None:
            self.m_audioSink.setVolume(value / 100.0)

    @Slot()
    def notified(self):
        bytes_free = self.m_audioSink.bytesFree()
        elapsed = self.m_audioSink.elapsedUSecs()
        processed = self.m_audioSink.processedUSecs()
        qWarning(f"bytesFree = {bytes_free}, "
                 f"elapsedUSecs = {elapsed}, "
                 f"processedUSecs = {processed}")

    @Slot()
    def pull_timer_expired(self):
        if self.m_audioSink is not None and self.m_audioSink.state() != QAudio.StoppedState:
            bytes_free = self.m_audioSink.bytesFree()
            data = self.m_generator.read(bytes_free)
            if data:
                self.m_output.write(data)

    @Slot()
    def toggle_mode(self):
        self.m_pullTimer.stop()
        self.m_audioSink.stop()

        if self.m_pullMode:
            self.m_modeButton.setText(self.PULL_MODE_LABEL)
            self.m_output = self.m_audioSink.start()
            self.m_pullMode = False
            self.m_pullTimer.start(20)
        else:
            self.m_modeButton.setText(self.PUSH_MODE_LABEL)
            self.m_pullMode = True
            self.m_audioSink.start(self.m_generator)

        self.m_suspendResumeButton.setText(self.SUSPEND_LABEL)

    @Slot()
    def toggle_suspend_resume(self):
        if self.m_audioSink.state() == QAudio.SuspendedState:
            qWarning("status: Suspended, resume()")
            self.m_audioSink.resume()
            self.m_suspendResumeButton.setText(self.SUSPEND_LABEL)
        elif self.m_audioSink.state() == QAudio.ActiveState:
            qWarning("status: Active, suspend()")
            self.m_audioSink.suspend()
            self.m_suspendResumeButton.setText(self.RESUME_LABEL)
        elif self.m_audioSink.state() == QAudio.StoppedState:
            qWarning("status: Stopped, resume()")
            self.m_audioSink.resume()
            self.m_suspendResumeButton.setText(self.SUSPEND_LABEL)
        elif self.m_audioSink.state() == QAudio.IdleState:
            qWarning("status: IdleState")

    state_map = {
        QAudio.ActiveState: "ActiveState",
        QAudio.SuspendedState: "SuspendedState",
        QAudio.StoppedState: "StoppedState",
        QAudio.IdleState: "IdleState"}

    @Slot(QAudio.State)
    def handle_state_changed(self, state):
        state = self.state_map.get(state, 'Unknown')
        qWarning(f"state = {state}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Output Test")

    devices = QMediaDevices.audioOutputs()
    if not devices:
        print('No audio outputs found.', file=sys.stderr)
        sys.exit(-1)

    audio = AudioTest(devices)
    audio.show()

    sys.exit(app.exec())
