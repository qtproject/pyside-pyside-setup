#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal, Slot
from helper.usesqapplication import UsesQApplication


class Listener(QObject):
    def __init__(self):
        super().__init__(None)
        self._phrase = []

    @Slot(tuple)
    def listen(self, words):
        for w in words:
            self._phrase.append(w)


class Communicate(QObject):
    # create a new signal on the fly and name it 'speak'
    speak = Signal(tuple)


class SignaltoSignalTest(UsesQApplication):
    def testBug(self):
        someone = Communicate()
        someone2 = Listener()
        # connect signal and slot
        someone.speak.connect(someone2.listen)
        # emit 'speak' signal
        talk = ("one", "two", "three")
        someone.speak.emit(talk)
        self.assertEqual(someone2._phrase, list(talk))


if __name__ == '__main__':
    unittest.main()

