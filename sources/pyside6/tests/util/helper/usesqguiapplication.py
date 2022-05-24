# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Helper classes and functions'''

import gc
import unittest

from PySide6.QtGui import QGuiApplication


class UsesQGuiApplication(unittest.TestCase):
    '''Helper class to provide QGuiApplication instances'''

    def setUp(self):
        '''Creates the QGuiApplication instance'''

        # Simple way of making instance a singleton
        super(UsesQGuiApplication, self).setUp()
        self.app = QGuiApplication.instance() or QGuiApplication([])

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(UsesQGuiApplication, self).tearDown()
