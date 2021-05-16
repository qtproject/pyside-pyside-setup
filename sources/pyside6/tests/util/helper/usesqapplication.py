# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Helper classes and functions'''

import gc
import sys
import unittest

# This version avoids explicit import in order to adapt to the
# import decision of the main module.
# This should work with every compatible library.

class UsesQApplication(unittest.TestCase):
    '''Helper class to provide QApplication instances'''

    qapplication = True

    def setUp(self):
        '''Creates the QApplication instance'''
        module = sys.modules[list(_ for _ in sys.modules if _.endswith(".QtWidgets"))[0]]
        QApplication = getattr(module, "QApplication")
        # Simple way of making instance a singleton
        super(UsesQApplication, self).setUp()
        self.app = QApplication.instance() or QApplication([])

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(UsesQApplication, self).tearDown()
