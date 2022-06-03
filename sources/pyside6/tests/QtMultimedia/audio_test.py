#############################################################################
##
## Copyright (C) 2016 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

'''Test cases for QHttp'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqguiapplication import UsesQGuiApplication
from PySide6.QtCore import QByteArray
from PySide6.QtMultimedia import QAudioBuffer, QAudioFormat, QMediaDevices


class testAudioDevices(UsesQGuiApplication):

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
