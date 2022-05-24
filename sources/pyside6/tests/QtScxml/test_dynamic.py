# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.timedqapplication import TimedQApplication
from PySide6.QtCore import QObject, SIGNAL
from PySide6.QtScxml import QScxmlStateMachine


class testDynamicStateMachine(TimedQApplication):
    def setUp(self):
        super(testDynamicStateMachine, self).setUp()
        filePath = os.path.join(os.path.dirname(__file__), 'trafficlight.scxml')
        self.assertTrue(os.path.exists(filePath))
        self._machine = QScxmlStateMachine.fromFile(filePath)
        self._machine.reachedStableState.connect(self._reachedStable())
        self.assertTrue(not self._machine.parseErrors())
        self.assertTrue(self._machine)

    def _reachedStable(self):
        self.app.quit()

    def test(self):
        self._machine.start()


if __name__ == '__main__':
    unittest.main()
