#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QTextToSpeech methods'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

try:
    from PySide6.QtTextToSpeech import QTextToSpeech, QVoice
except ImportError:
    print("Skipping test due to missing QtTextToSpeech module")
    sys.exit(0)


class QTextToSpeechTestCase(UsesQApplication):
    '''Tests related to QTextToSpeech'''
    def testSay(self):
        engines = QTextToSpeech.availableEngines()
        if len(engines) > 1 and engines[0] == "mock":
            engines[0], engines[1] = engines[1], engines[0]
        if not engines:
            print('No QTextToSpeech engines available')
        else:
            speech = QTextToSpeech(engines[0])
            speech.stateChanged.connect(self._slotStateChanged)
            speech.say("Hello, PySide6")
            QTimer.singleShot(5000, self.app.quit)
            self.app.exec()

    def _slotStateChanged(self, state):
        if (state == QTextToSpeech.State.Ready):
            self.app.quit()


if __name__ == '__main__':
    unittest.main()
