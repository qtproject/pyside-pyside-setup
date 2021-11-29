#!/usr/bin/python

#############################################################################
##
## Copyright (C) 2016 The Qt Company Ltd.
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

'''Test cases for QThread'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QThread, QCoreApplication, QObject, QTimer, Slot
from PySide6.QtCore import QEventLoop

from helper.usesqcoreapplication import UsesQCoreApplication


class Dummy(QThread):
    '''Dummy thread'''
    def __init__(self, *args):
        super().__init__(*args)
        self.called = False

    def run(self):
        # Start-quit sequence
        self.qobj = QObject()
        self.called = True


class QThreadSimpleCase(UsesQCoreApplication):

    def setUp(self):
        UsesQCoreApplication.setUp(self)
        self._started_called = False
        self._finished_called = False
        self.called = False

    def testThread(self):
        # Basic QThread test
        obj = Dummy()
        obj.start()
        self.assertTrue(obj.wait(100))

        self.assertTrue(obj.called)

    @Slot()
    def abort_application(self):
        if self._thread.isRunning():
            print("Warning: terminating thread", file=sys.stderr)
            self._thread.terminate()
        self.app.quit()

    @Slot()
    def finished(self):
        self._finished_called = True

    @Slot()
    def started(self):
        self._started_called = True

    def testSignals(self):
        # QThread.finished() (signal)
        self._thread = Dummy()
        self._thread.started.connect(self.started)
        self._thread.finished.connect(self.finished)
        self._thread.finished.connect(self.app.quit)

        QTimer.singleShot(50, self._thread.start)
        QTimer.singleShot(1000, self.abort_application)

        self.app.exec()
        if self._thread.isRunning():
            self._thread.wait(100)

        self.assertTrue(self._started_called)
        self.assertTrue(self._finished_called)


if __name__ == '__main__':
    unittest.main()
