# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Helper classes and functions'''

import gc
import unittest

from PySide6.QtWidgets import QApplication


class UsesQApplication(unittest.TestCase):
    '''Helper class to provide QApplication instances'''

    qapplication = True

    def setUp(self):
        '''Creates the QApplication instance'''

        # Simple way of making instance a singleton
        super(UsesQApplication, self).setUp()
        self.app = QApplication.instance() or QApplication([])

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(UsesQApplication, self).tearDown()
