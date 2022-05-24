# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QSignalMapper
from PySide6.QtWidgets import QCheckBox

from helper.usesqapplication import UsesQApplication


class MultipleSlotTest(UsesQApplication):
    def cb_changed(self, i):
        self._changed = True

    def cb_changedVoid(self):
        self._changed = True

    def testSignalMapper(self):
        checkboxMapper = QSignalMapper()
        box = QCheckBox('check me')
        box.stateChanged.connect(checkboxMapper.map)

        checkboxMapper.setMapping(box, box.text())
        checkboxMapper.mappedString[str].connect(self.cb_changed)
        self._changed = False
        box.setChecked(True)
        self.assertTrue(self._changed)

    def testSimpleSignal(self):
        box = QCheckBox('check me')
        box.stateChanged[int].connect(self.cb_changedVoid)
        self._changed = False
        box.setChecked(True)
        self.assertTrue(self._changed)


if __name__ == '__main__':
    unittest.main()
