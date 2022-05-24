# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Helper classes and functions'''

import gc
import unittest

from PySide6.QtCore import QCoreApplication

_core_instance = None


class UsesQCoreApplication(unittest.TestCase):
    '''Helper class for test cases that require an QCoreApplication
    Just connect or call self.exit_app_cb. When called, will ask
    self.app to exit.
    '''

    def setUp(self):
        '''Set up resources'''

        global _core_instance
        if _core_instance is None:
            _core_instance = QCoreApplication([])

        self.app = _core_instance

    def tearDown(self):
        '''Release resources'''
        del self.app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def exit_app_cb(self):
        '''Quits the application'''
        self.app.exit(0)
