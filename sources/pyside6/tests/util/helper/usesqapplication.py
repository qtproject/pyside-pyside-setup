# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Helper classes and functions'''

import gc
import sys
import unittest

# This version avoids explicit import in order to adapt to the
# import decision of the main module.
# This should work with every compatible library.
# Replaces the QtGui and QtCore versions as well.

class UsesQApplication(unittest.TestCase):
    '''Helper class to provide Q(Core|Gui|)Application instances
    Just connect or call self.exit_app_cb. When called, will ask
    self.app to exit.
    '''

    def setUp(self):
        '''Creates the QApplication instance'''
        module = sys.modules[sorted(_ for _ in sys.modules
                                    if _.endswith((".QtCore", ".QtGui", ".QtWidgets")))[-1]]
        found = module.__name__.rsplit(".")[-1]
        cls = getattr(module, {"QtWidgets": "QApplication",
                               "QtGui":     "QGuiApplication",
                               "QtCore":    "QCoreApplication"}[found])
        # Simple way of making instance a singleton
        super().setUp()
        self.app = cls.instance() or cls([])

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.app
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super().tearDown()

    def exit_app_cb(self):
        '''Quits the application'''
        self.app.exit(0)
