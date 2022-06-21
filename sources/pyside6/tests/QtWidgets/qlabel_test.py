# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QLabel'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel
from shiboken6 import Shiboken

from helper.usesqapplication import UsesQApplication


class QLabelTest(UsesQApplication):
    '''Test case for calling QLabel.setPixmap'''

    def setUp(self):
        super(QLabelTest, self).setUp()
        self.label = QLabel()

    def tearDown(self):
        del self.label
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(QLabelTest, self).tearDown()

    def testSetPixmap(self):

        p1 = QPixmap(5, 5)
        p2 = QPixmap(10, 10)

        self.label.setPixmap(p1)
        self.assertIsNotNone(self.label.pixmap())

        # PYSIDE-150:
        #   When a new QPixmap is assigned to a QLabel,
        #   the previous one needs to be cleared.
        #   This means we should not keep a copy of the QPixmap
        #   on Python-side.

        # Getting pointer to the QPixmap
        ret_p = self.label.pixmap()
        self.assertIsNot(p1, ret_p)
        # Save the address of the pointer
        ret_p_addr = Shiboken.getCppPointer(ret_p)
        # Remove the QPixmap
        del ret_p
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        # Set new QPixmap
        self.label.setPixmap(p2)

        # There should be no pointers remaining with the same
        # address that our QPixmap p1 because it was deleted
        # using `del ret_p`
        self.assertTrue(all(Shiboken.getCppPointer(o) != ret_p_addr
                   for o in Shiboken.getAllValidWrappers()))

    # Test for PYSIDE-1673, QObject.property() returning a QFlags<> property.
    def testQObjectProperty(self):
        a = self.label.property("alignment")
        self.assertEqual(type(a), Qt.Alignment)
        print("alignment=", a)


if __name__ == '__main__':
    unittest.main()
