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

from helper.usesqguiapplication import UsesQGuiApplication
from PySide6.QtMultimedia import QAudioDevice, QAudioFormat, QMediaDevices


class testAudioDevices(UsesQGuiApplication):

    def testListDevices(self):
        valid = False
        devices = QMediaDevices.audioOutputs()
        if not len(devices):
            return

        valid = True
        for dev_info in devices:
            if dev_info.id() == 'null':
                # skip the test if the only device found is a invalid device
                if len(devices) == 1:
                    return
                else:
                    continue
            fmt = QAudioFormat()
            for sample_format in dev_info.supportedSampleFormats():
                fmt.setSampleFormat(sample_format)
                fmt.setChannelCount(dev_info.maximumChannelCount())
                fmt.setSampleRate(dev_info.maximumSampleRate())
                self.assertTrue(dev_info.isFormatSupported(fmt))


if __name__ == '__main__':
    unittest.main()
