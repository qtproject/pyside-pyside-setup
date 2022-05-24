# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Helper classes and functions'''

import gc
import unittest

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication


class TimedQGuiApplication(unittest.TestCase):
    '''Helper class with timed QGuiApplication exec loop'''

    def setUp(self, timeout=100):
        '''Sets up this Application.

        timeout - timeout in millisseconds'''
        self.app = QGuiApplication.instance() or QGuiApplication([])
        QTimer.singleShot(timeout, self.app.quit)

    def tearDown(self):
        '''Delete resources'''
        del self.app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
