#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

'''Test paint event override in python'''

import gc
import os
import sys
import unittest

from textwrap import dedent

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget

from helper.usesqapplication import UsesQApplication


class MyWidget(QWidget):
    '''Sample widget'''

    def __init__(self, app):
        # Creates a new widget
        assert(app)

        super().__init__()
        self.app = app
        self.paint_event_called = False

    def paintEvent(self, event):
        # Empty paint event method
        super().paintEvent(event)
        self.paint_event_called = True
        QTimer.singleShot(20, self.close)


class PaintEventOverride(UsesQApplication):
    '''Test case for overriding QWidget.paintEvent'''

    qapplication = True

    def setUp(self):
        # Acquire resources
        super(PaintEventOverride, self).setUp()
        self.widget = MyWidget(self.app)

    def tearDown(self):
        # Release resources
        del self.widget
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(PaintEventOverride, self).tearDown()

    def testPaintEvent(self):
        # Test QWidget.paintEvent override
        self.widget.show()
        self.widget.setWindowTitle("paint_event_test")
        self.app.exec()
        self.assertTrue(self.widget.paint_event_called)


if __name__ == '__main__':
    unittest.main()
