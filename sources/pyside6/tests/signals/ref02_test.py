#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QTimeLine
from helper.usesqapplication import UsesQApplication


class NativeSignalsTest(UsesQApplication):

    def setUp(self):
        UsesQApplication.setUp(self)
        self.called = False
        self.timeline = QTimeLine(100)

    def tearDown(self):
        del self.called
        del self.timeline
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        UsesQApplication.tearDown(self)

    def testSignalWithIntArgument(self):

        def valueChangedSlot(value):
            self.called = True
            self.assertEqual(type(value), float)
            self.app.quit()

        self.timeline.valueChanged.connect(valueChangedSlot)
        self.timeline.start()

        self.app.exec()
        self.assertTrue(self.called)

    def testSignalWithoutArguments(self):

        def finishedSlot():
            self.called = True
            self.app.quit()

        self.timeline.finished.connect(finishedSlot)
        self.timeline.start()

        self.app.exec()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()

