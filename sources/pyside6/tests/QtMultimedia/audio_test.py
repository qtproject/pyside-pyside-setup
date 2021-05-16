# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QHttp'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QByteArray
from PySide6.QtMultimedia import QAudioBuffer, QAudioFormat, QMediaDevices


class testAudioDevices(UsesQApplication):

    def setUp(self):
        super().setUp()
        self._devices = []
        for d in QMediaDevices.audioOutputs():
            if d:
                self._devices.append(d)

    def test_list_devices(self):
        if not self._devices:
            print("No audio outputs found")
            return

        for dev_info in self._devices:
            print("Testing ", dev_info.id())
            fmt = QAudioFormat()
            for sample_format in dev_info.supportedSampleFormats():
                fmt.setSampleFormat(sample_format)
                fmt.setChannelCount(dev_info.maximumChannelCount())
                fmt.setSampleRate(dev_info.maximumSampleRate())
                self.assertTrue(dev_info.isFormatSupported(fmt))

    def test_audiobuffer(self):
        """PYSIDE-1947: Test QAudioBuffer.data()."""
        if not self._devices:
            print("No audio outputs found")
            return
        size = 256
        byte_array = QByteArray(size, '7')
        buffer = QAudioBuffer(byte_array, self._devices[0].preferredFormat())
        self.assertEqual(buffer.byteCount(), 256)
        data = buffer.data()
        actual_byte_array = QByteArray(bytearray(data))
        self.assertEqual(byte_array, actual_byte_array)


if __name__ == '__main__':
    unittest.main()
